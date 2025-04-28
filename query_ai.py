from openai import OpenAI
import ccxt
import os
import pandas as pd

OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

# Binance 선물 거래소 초기화
exchange = ccxt.binance({
  'options': {
    'defaultType': 'future' ## 선물 거래소로 설정
  }
})

# 차트 데이터 가져오기
ohlcv = exchange.fetch_ohlcv('BTC/USDT', timeframe='15m', limit=96)
df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

cols = ['open', 'high', 'low', 'close', 'volume']
df[cols] = df[cols].round(1).astype(int)
print(df)

# OpenAI에 질의하기
# client = OpenAI(api_key=OPENAI_API_KEY)
# response = client.responses.create(
#   model="o4-mini",
#   input=[
#     {
#       "role": "developer",
#       "content": [
#         {
#           "type": "input_text",
#           "text": "You're a crypto trading expert. Analyze market data and tell me the prices of the support and resistance lines"
#         }
#       ]
#     },
#     {
#       "role": "user",
#       "content": [
#         {
#           "type": "input_text",
#           "text": df.to_json()
#         }
#       ]
#     },
#     {
#       "role": "assistant",
#       "content": [
#         {
#           "type": "output_text",
#           "text": "Long"
#         }
#       ]
#     },
#   ],
#   reasoning={
#     "effort": "medium"
#   },
# )

# print(response.output[1].content[0].text)