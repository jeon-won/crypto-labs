# from datetime import datetime
# from api.common import convert_unixtime_to_datetime
from api.ohlcv_analyzer import is_tail_candles
from api.messenger import send_discord_message
from pprint import pprint
import ccxt, json, os

# 함수 --------------------------------------------------

def check_timeframe(timeframe):
    """타임 프레임을 체크하여 다음 조건을 만족하는지 판단합니다.

    - (조건 1) 5m과 15m이 포함된 경우
    - (조건 2) 15m이 있으면서 1h, 2h, 4h 중 적어도 하나 있는 경우

    :return: 조건을 만족하면 True, 그렇지 않으면 False
    """
    if "5m" in timeframe and "15m" in timeframe:
        return True
    if "15m" in timeframe and any(t in timeframe for t in ["1h", "2h", "4h"]):
        return True
    return False

# 상수 --------------------------------------------------

SYMBOL = "BTC/USDT"
LIMIT = 2
TIMEFRAME = ["3m", "5m", "15m", "1h", "2h", "4h"]

# 변수 --------------------------------------------------

tailed_timeframe = []
binance = ccxt.binance(config={
    'options': {
        'defaultType': 'future'
    }
})

# 코드 --------------------------------------------------

for tf in TIMEFRAME:
    ohlcv = binance.fetch_ohlcv(SYMBOL, tf, limit=LIMIT)
    asdf = is_tail_candles(ohlcv, 1.2, 2)
    if(asdf):
        tailed_timeframe.append(tf)

is_timimg = check_timeframe(tailed_timeframe)
print(tailed_timeframe)
print(is_timimg)