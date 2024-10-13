from pymongo import MongoClient
import ccxt
from pprint import pprint
from datetime import datetime

# 상수
MONGO_ID = "admin"          ## MongoDB 접속 ID
MONGO_PASSWORD = "password" ## MongoDB 접속 비밀번호
MONGO_IP = "localhost"      ## MongoDB 접속 주소
MONGO_PORT = "27017"        ## MongoDB 포트
MONGO_DB = "ohlcv"          ## MongoDB 이름

# 초기화
binance = ccxt.binance()
client = MongoClient(f"mongodb://{MONGO_ID}:{MONGO_PASSWORD}@{MONGO_IP}:{MONGO_PORT}/?authSource={MONGO_DB}")
db = client[MONGO_DB]
collection = db["btc_15m"]

# BTC 15분봉 최근 5개의 캔들 정보를 DB에 저장
ohlcv = binance.fetch_ohlcv("BTC/USDT", "15m", limit=5)
for item in ohlcv:
  data = {
    "time": datetime.fromtimestamp(item[0] / 1000),
    "open": item[1],
    "how": item[2],
    "low": item[3],
    "close": item[4],
    "volume": item[5]
  }
  insert_result = collection.insert_one(data)
  pprint(insert_result)