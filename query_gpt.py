from api.common import save_current_time, load_time
from api.messenger import send_discord_message
from datetime import datetime
from dotenv import load_dotenv
import api.ohlcv_analyzer_v1 as oa
import ccxt, openai, os
"""
# query_gpt.py
* 기능: 특정 타이밍이 왔을 때 OpenAI API를 사용하여 비트코인 포지션을 잡아도 될지 질의합니다.
* 사용법: query_gpt.py 파일 실행
"""

# 상수
load_dotenv()
DISCORD_WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
MODEL_NAME = "o3-mini"  ## gpt-4o, gpt-4o-mini, o1-mini 등
SYMBOL = 'BTC/USDT'
LIMIT = 200             ## 가져올 캔들 개수
MULTIPLIER = 3          ## 거래량, 캔들크기가 평균 대비 몇 배 이상일 떄 OpenAI에 질의할 것인지?

binance = ccxt.binance(config={
    'options': {
        'defaultType': 'future'
    }
})
ohlcv = binance.fetch_ohlcv(SYMBOL, '15m', limit=LIMIT)
current_price = ohlcv[-1][4]
transformed_ohlcv = []

# 입력 토큰 절감을 위해 Unixtime 자릿수는 순서번호(인덱스)로 변경하고, 그 외 데이터는 반올림 함
for i, row in enumerate(ohlcv, start=1):
    values = [round(value) for value in row[1:]]  # 나머지 요소는 반올림
    transformed_ohlcv.append([i] + values) # 첫 번째 요소 대신 순서 번호(i)를 사용

# 여러 데이터 저장
## 현재 거래량, 캔들크기 및 RSI 값 저장
current_vol_15m = ohlcv[-1][5]
current_candle_size_15m = abs(((ohlcv[-1][4] - ohlcv[-1][1]) / ohlcv[-1][1]) * 100)
current_rsi_15m = oa.calculate_rsi(ohlcv)
## 평균 거래량 및 캔들크기 저장
avg_vol_15 = oa.get_avg_volume(ohlcv)
avg_candle_size_15m = oa.get_avg_candle_size(ohlcv)

prompt = f"""
# Things to do
Please analyze the the current Bitcoin chart candlestick pattern if it fits the patterns below. Assume that if the pattern below fits more than two, there is a high probability of making a profit.
- When the current trading volume is significantly higher (5 times or more) than the previous candlesticks and the candle length is very long or very short
- Currently candlestick reaches support or resistance line (Inference is required for support or resistance line)
- Currently bullish divergence or bearish divergence occured
- Currently multiple (more than two) Hammer candlestick or inverted hammer candlestick pattern occured
- Currently Doji candles accompanied by trading volume occured
- Currently Three Black Crows or Three White Soldiers occured
- If you know any other bitcoin chart candlestick patterns, please let me know

# Data
The data below is a processing of the OHLCV data of Bitcoin returned by python ccxt's fetch_ohlcv() function. The first element of each array is the index (the higher the value, the latest candlestick), followed by the market price, high price, low price, closing price, and trading volume.
* the current RSI value: {current_rsi_15m}.
* OHLCV data: {transformed_ohlcv}

# Answer
Based on the analysis above, please let me know if I can buy bitcoin now. Please tell us the answer in the JSON format below.
{{
  "time": "{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}",
  "recommended_position": "(Choose from Long, Short or No position)", 
  "analysis_result": "(Analysis results of the the current Bitcoin chart candlestick pattern. Please answer in short answer format and translate this part into Korean.)",
  "support_line": "(support line price. No more than 3)",
  "resistance_line": "(resistance line price. No more than 3)"
}}
"""

# 현재시간과 이전 질의시간 차이 계산(59분 미만이면 질의하지 않음)
script_dir = os.path.dirname(os.path.abspath(__file__))
time_file_path = os.path.join(script_dir, "time.txt")
time_previous = load_time(time_file_path)
time_current = datetime.now()
time_diff = time_current - time_previous
time_diff_minutes = time_diff.total_seconds() / 60

# OpenAI에 질의할 타이밍이면 질의
is_timing = (time_diff_minutes >= 59) and \
    ((current_vol_15m >= avg_vol_15 * MULTIPLIER) or \
    (current_candle_size_15m >= avg_candle_size_15m * MULTIPLIER) or \
    (current_rsi_15m <= 30 or current_rsi_15m >= 70))

if(is_timing):
    response = openai.chat.completions.create(
        model=MODEL_NAME,  # 사용할 모델
        messages=[
            {"role": "system", "content": "You are a bitcoin day trading expert who makes a profit from reverse trend trading."},  # 시스템 메시지. o1-mini에선 사용 안 함.
            {"role": "user", "content": prompt},  # 사용자 입력
        ],
        reasoning_effort="high", # o3-mini 모델에서만 사용하는 옵션: "low", "medium", "high"
        # max_tokens=150, # 최대 토큰 수. o3-mini 모델은 지원 안 함.
        # temperature=0,  # 응답의 창의성 정도. o1-mini는 1만 사용 가능.
    )
    # 질의 시간 기록
    save_current_time("time.txt")
    # 응답 출력
    print(response.choices[0].message.content)
    send_discord_message(DISCORD_WEBHOOK_URL, response.choices[0].message.content)