import api.ohlcv_analyzer as oa
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

prompt = f"""You are a Bitcoin Day trading investor. The data below is a processing of the OHLCV data of Bitcoin returned by python ccxt's fetch_ohlcv() function. The first element of each array is the index (the higher the value, the latest candle), followed by the market price, high price, low price, closing price, and trading volume.

{transformed_ohlcv_15m}

the current RSI value is {current_rsi_15m}.

After analyzing chart patterns, support lines, resistance lines, diversions, etc., please let me know if I can make a profit by Day trading if I get a position (long, short) right now. 

Please answer in the Markdown format below.
# {datetime.now().strftime("%Y-%m-%d %H:%M:%S")} Bitcoin Position Judgment
* Decision: (Decided to be long, short or wait-and-see)
* Reason: (Base of Judgment)
* Support Line Analysis Results: (Price of Support Line or Resistance line price)

Please tell us the answer in Korean only.
"""

# OpenAI에 질의할 타이밍이면 질의
is_timing = (current_vol_15m >= avg_vol_15 * MULTIPLIER) or \
    (current_candle_size_15m >= avg_candle_size_15m * MULTIPLIER) or \
    (current_rsi_15m <= 30 or current_rsi_15m >= 70)
if(True):
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
