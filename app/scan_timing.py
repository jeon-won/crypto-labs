# from datetime import datetime
# from api.common import convert_unixtime_to_datetime
from api import ohlcv_analyzer
from api.messenger import send_discord_message
from pprint import pprint
import ccxt, json, os

# 함수 --------------------------------------------------
def check_timeframes(dictionary):
    # 찾고자 하는 필수 timeframes
    required_values = {'15m', '1h', '2h', '4h', '12h', '1d'}
    
    # 딕셔너리의 모든 값들을 집합으로 변환하여 중복을 제거하고 포함 여부를 확인
    all_values = set(value for values in dictionary.values() for value in values)
    
    # '15m'이 반드시 포함되어 있어야 하고, 그 외 필요한 값 중 하나라도 포함되면 True 반환
    return '15m' in all_values and bool(all_values & required_values)

# 상수 --------------------------------------------------
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")
SYMBOL = "BTC/USDT"
LIMIT = 100
TIMEFRAME = ["1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "12h", "1d"]
binance = ccxt.binance(config={
    'options': {
        'defaultType': 'future'
    }
})

# 변수 --------------------------------------------------
avg_candle = {}  ## 각 분봉의 평균 캔들 크기 저장
avg_vol = {}     ## 각 분봉의 평균 거래량 저장
candle_info = {  ## 각 분봉의 3틱 생성, 여러꼬리 캔들, 겁나 큰 캔들 또는 거래량 생성 여부 저장
    "is_three_tick": [],
    "is_tail_candles": [],
    "is_big_candle_size": [],
    "is_big_volume": []
}
for tf in TIMEFRAME:  ## 평균 캔들, 거래량 딕셔너리에 키 생성
  avg_candle[tf] = ''
  avg_vol[tf] = ''

ohlcv = {}
for tf in TIMEFRAME:
    ohlcv[tf] = binance.fetch_ohlcv(SYMBOL, tf, limit=LIMIT)
    avg_candle[tf] = ohlcv_analyzer.get_avg_candle_size(ohlcv[tf])
    avg_vol[tf] = ohlcv_analyzer.get_avg_volume(ohlcv[tf])
    
    if(ohlcv_analyzer.is_three_tick(ohlcv[tf][-3:], avg_candle[tf])):
       candle_info["is_three_tick"].append(tf)
    if(ohlcv_analyzer.is_tail_candles(ohlcv[tf][-3:], 1.1, 2)):
       candle_info["is_tail_candles"].append(tf)
    if(ohlcv_analyzer.is_big_candle_size(ohlcv[tf][-1], avg_candle[tf], 30)):
       candle_info["is_big_candle_size"].append(tf)
    if(ohlcv_analyzer.is_big_volume(ohlcv[tf][-1], avg_vol[tf], 3)):
       candle_info["is_big_volume"].append(tf)

pprint(candle_info)
print(check_timeframes(candle_info))

is_timimg = check_timeframes(candle_info)
if(is_timimg):
    send_discord_message(DISCORD_WEBHOOK_URL, str(json.dumps(candle_info, indent=4)))