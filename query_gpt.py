import api.ohlcv_analyzer_v1 as oa
from api.common import save_time, load_time
import ccxt
import os
import openai
from api.messenger import send_discord_message
from datetime import datetime
from dotenv import load_dotenv

# 상수
load_dotenv()
DISCORD_WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
MODEL_NAME = "o1-mini"  ## gpt-4o, gpt-4o-mini, o1-mini 등
SYMBOL = 'BTC/USDT'
LIMIT = 200             ## 가져올 캔들 개수
MULTIPLIER = 3          ## 거래량, 캔들크기가 평균 대비 몇 배 이상일 떄 OpenAI에 질의할 것인지?

# 비트코인 두 캔들의 ohlcv 값 가져오기
binance = ccxt.binance(config={
    'options': {
        'defaultType': 'future'
    }
})

ohlcv_15m = binance.fetch_ohlcv(SYMBOL, '15m', limit=LIMIT)
current_price = ohlcv_15m[-1][4]
transformed_ohlcv_15m = []

# 입력 토큰 절감을 위해 Unixtime 자릿수는 순서번호(인덱스)로 변경하고, 그 외 데이터는 반올림 함
for i, row in enumerate(ohlcv_15m, start=1):
    values = [round(value) for value in row[1:]]  # 나머지 요소는 반올림
    transformed_ohlcv_15m.append([i] + values) # 첫 번째 요소 대신 순서 번호(i)를 사용

# 여러 데이터 저장
## 현재 거래량, 캔들크기 및 RSI 값 저장
current_vol_15m = ohlcv_15m[-1][5]
current_candle_size_15m = abs(((ohlcv_15m[-1][4] - ohlcv_15m[-1][1]) / ohlcv_15m[-1][1]) * 100)
current_rsi_15m = oa.calculate_rsi(ohlcv_15m)
## 평균 거래량 및 캔들크기 저장
avg_vol_15 = oa.get_avg_volume(ohlcv_15m)
avg_candle_size_15m = oa.get_avg_candle_size(ohlcv_15m)

prompt = f"""
# Role
You are a bitcoin day trading investor who makes a profit from reverse trend trading.

# Things to do
Please analyze the the current Bitcoin chart candlestick pattern if it fits the patterns below.
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
* OHLCV data: {transformed_ohlcv_15m}

# Answer
Based on the analysis above, please let me know if I can buy bitcoin now. Please tell us the answer in the JSON format below.
{{
  "time": "{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}",
  "pattern_analysis_result": "(Analysis results of the the current Bitcoin chart candlestick pattern. Please translate this part into Korean.)",
  "support_line": "(support line price)",
  "resistance_line": "(resistance line price)"
}}
"""

# OpenAI에 질의할 타이밍이면 질의
is_timing = (current_vol_15m >= avg_vol_15 * MULTIPLIER) or \
    (current_candle_size_15m >= avg_candle_size_15m * MULTIPLIER) or \
    (current_rsi_15m <= 30 or current_rsi_15m >= 70)
if(is_timing):
    response = openai.chat.completions.create(
        model=MODEL_NAME,  # 사용할 모델
        messages=[
            # {"role": "system", "content": "You are a Bitcoin Day trading investor."},  # 시스템 메시지. o1-mini에선 사용 안 함.
            {"role": "user", "content": prompt},  # 사용자 입력
        ],
        # max_tokens=150,  # 최대 토큰 수
        # temperature=0,  # 응답의 창의성 정도. o1-mini는 1만 사용 가능.
    )
    # 응답 출력
    print(response.choices[0].message.content)
    send_discord_message(DISCORD_WEBHOOK_URL, response.choices[0].message.content)
