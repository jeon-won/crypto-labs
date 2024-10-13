import ccxt
from pprint import pprint
import time

timeframe = ["5m", "15m", "30m", "1h"]
dic = {
  '5m': 1,
  '15m': 2,
  '30m': 3,
  '1h': 4
}

for tf in timeframe:
  print(dic[tf])



# binance = ccxt.binance()
# binance.fetch_ohlcv("BTC/USDT", "5m", limit=5)