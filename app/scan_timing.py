from api import ohlcv_analyzer
from api.common import convert_unixtime_to_datetime
from api.messenger import send_discord_message
from datetime import datetime
import ccxt
import time
from pprint import pprint

# TODO 비트코인 매수하기 좋아 보이는 타이밍 스캔
#  * 장기(1D, 12H), 중기(4H, 2H, 1H) 및 단기(30M, 15M, 5M) 캔들로 나눠서 진행
#  * 3틱, 현재 장대봉, 꼬리캔들 생성 여부 등을 스캔

SYMBOL = "BTC/USDT"
LIMIT = 100
TIMEFRAME = ["5m", "15m", "30m", "1h", "2h", "4h", "12h", "1d"]
binance = ccxt.binance(config={
    'options': {
        'defaultType': 'future'
    }
})

# 변수
avg_candle = {}  ## 각 분봉의 평균 캔들 크기 저장
avg_vol = {}     ## 각 분봉의 평균 거래량 저장
candle_info = {  ## 각 분봉의 3틱 생성, 여러꼬리 캔들, 겁나 큰 캔들 또는 거래량 생성 여부 저장
    "is_three_tick": {},
    "is_tail_candles": {},
    "is_big_candle_size": {},
    "is_big_volume": {}
}
for tf in TIMEFRAME:  ## 평균 캔들, 거래량 딕셔너리에 키 생성
  avg_candle[tf] = ''
  avg_vol[tf] = ''


# 데이터 가공
## ohlcv 데이터 가져오기
ohlcv = {}
count = 0
for tf in TIMEFRAME:
    ohlcv[tf] = binance.fetch_ohlcv(SYMBOL, tf, limit=LIMIT)
    avg_candle[tf] = ohlcv_analyzer.get_avg_candle_size(ohlcv[tf])
    avg_vol[tf] = ohlcv_analyzer.get_avg_volume(ohlcv[tf])
    
    if(ohlcv_analyzer.is_three_tick(ohlcv[tf][-5:], avg_candle[tf])):
       candle_info["is_three_tick"] = tf
       count += 1
    if(ohlcv_analyzer.is_tail_candles(ohlcv[tf][-2:], 1.1, 2)):
       candle_info["is_tail_candles"] = tf
       count += 1
    if(ohlcv_analyzer.is_big_candle_size(ohlcv[tf][-1], avg_candle[tf], 30)):
       candle_info["is_big_candle_size"] = tf
       count += 1
    if(ohlcv_analyzer.is_big_volume(ohlcv[tf][-1], avg_vol[tf], 3)):
       candle_info["is_big_volume"] = tf
       count += 1

pprint(candle_info)
pprint(count)