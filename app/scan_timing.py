from api import ccxt_analyzer
from api.common import convert_unixtime_to_datetime
from api.messenger import send_discord_message
from datetime import datetime
import ccxt
import time

# TODO 비트코인 매수하기 좋아 보이는 타이밍 스캔
#  * 장기(1D, 12H), 중기(4H, 2H, 1H) 및 단기(30M, 15M, 5M) 캔들로 나눠서 진행
#  * 3틱, 현재 장대봉, 꼬리캔들 생성 여부 등을 스캔

SYMBOL = "BTC/USDT"
LIMIT = 50
binance = ccxt.binance(config={
    'options': {
        'defaultType': 'future'
    }
})
info_btc = { "5m": {}, "15m": {}, "30m": {}, "1h": {}, "2h": {}, "1h": {}, "1d": {} }

def set_btc_info(timeframe, ohlcv, options={
    "std_ratio": 1.2,  # 꼬리-몸통 크기 비율
    "std_num": 2,    # 꼬리 캔들 개수 
    "multiple_candle": 3,   # 배수
    "multiple_vol": 4,   # 배수
}):
    data = {
        timeframe: {}
    }
    data[timeframe]["time"] = str(datetime.now())
    data[timeframe]["avg_candle_size"] = ccxt_analyzer.get_avg_candle_size(ohlcv)
    data[timeframe]["avg_vol"] = ccxt_analyzer.get_avg_volume(ohlcv)
    data[timeframe]["is_three_tick"] = ccxt_analyzer.is_three_tick(ohlcv[-1:-6:-1], data[timeframe]["avg_vol"])
    data[timeframe]["is_tail_candles"] = ccxt_analyzer.is_tail_candles(ohlcv[-1:-3:-1], options["std_ratio"], options["std_num"])
    data[timeframe]["is_big_candle_size"] = ccxt_analyzer.is_big_candle_size(ohlcv[-1], data[timeframe]["avg_vol"], options["multiple_candle"])
    data[timeframe]["is_big_volume"] = ccxt_analyzer.is_big_volume(ohlcv[-1], data[timeframe]["avg_vol"], options["multiple_vol"])
    return data

while True:
    current_time = datetime.now()

    # 5분 봉: 마감 10초 전 -> 현재 분을 5로 나눈 나머지가 4이고, 현재 초가 50초 이상인 경우
    if(current_time.minute % 5 == 4 and 50 <= current_time.second < 60):
        ohlcv = binance.fetch_ohlcv(SYMBOL, "5m", limit=LIMIT)
        info_btc = set_btc_info("5m", ohlcv)
        print(info_btc)
        time.sleep(10)
        continue

    # 15분 봉: 마감 20초 전 -> 현재 분을 15로 나눈 나머지가 14이고, 현재 초가 40초 이상인 경우
    if(current_time.minute % 15 == 14 and 40 <= current_time.second < 50):
        ohlcv = binance.fetch_ohlcv(SYMBOL, "15m", limit=LIMIT)
        info_btc = set_btc_info("15m", ohlcv)
        print(info_btc)
        time.sleep(10)
        continue

    # 30분 봉: 마감 30초 전 -> 현재 분을 30으로 나눈 나머지가 29이고, 현재 초가 30초 이상인 경우
    if(current_time.minute % 30 == 29 and 30 <= current_time.second < 40):
        ohlcv = binance.fetch_ohlcv(SYMBOL, "30m", limit=LIMIT)
        info_btc = set_btc_info("30m", ohlcv)
        print(info_btc)
        time.sleep(10)
        continue

    # 1시간 봉: 마감 40초 전 -> 현재 분이 59분 이고, 현재 초가 20초 이상인 경우
    if(current_time.minute == 59 and 20 <= current_time.second < 30):
        ohlcv = binance.fetch_ohlcv(SYMBOL, "1h", limit=LIMIT)
        info_btc = set_btc_info("1h", ohlcv)
        print(info_btc)
        time.sleep(10)
        continue

    # 2시간 봉: 마감 50초 전 -> 현재 시간을 2로 나눈 나머지가 0이고, 현재 분이 59분 이고, 현재 초가 10초 이상인 경우
    if(current_time.hour % 2 == 0 and current_time.minute == 59 and 10 <= current_time.second < 20):
        ohlcv = binance.fetch_ohlcv(SYMBOL, "2h", limit=LIMIT)
        info_btc = set_btc_info("2h", ohlcv)
        print(info_btc)
        time.sleep(10)
        continue

    # 4시간 봉: 마감 1분 전 -> 현재 시간을 4로 나눈 나머지가 0이고, 현재 분이 59분 이고, 현재 초가 0초 이상인 경우
    if(current_time.hour % 4 == 0 and current_time.minute == 59 and 0 <= current_time.second < 10):
        ohlcv = binance.fetch_ohlcv(SYMBOL, "4h", limit=LIMIT)
        info_btc = set_btc_info("4h", ohlcv)
        print(info_btc)
        time.sleep(10)
        continue

    # 12시간 봉: 마감 1분 10초 전 -> 현재 시간을 12로 나눈 나머지가 0이고, 현재 분이 58분 이고, 현재 초가 50초 이상인 경우
    if(current_time.hour % 12 == 0 and current_time.minute == 58 and 50 <= current_time.second < 60):
        ohlcv = binance.fetch_ohlcv(SYMBOL, "12h", limit=LIMIT)
        info_btc = set_btc_info("12h", ohlcv)
        print(info_btc)
        time.sleep(10)
        continue

    # 1일 봉: 마감 1분 20초 전 -> 현재 시간이 8시, 현재 분이 58분 이고, 현재 초가 40초 이상인 경우
    if(current_time.hour == 8 and current_time.minute == 58 and 40 <= current_time.second < 50):
        ohlcv = binance.fetch_ohlcv(SYMBOL, "1d", limit=LIMIT)
        info_btc = set_btc_info("1d", ohlcv)
        print(info_btc)
        time.sleep(10)
        continue

    # print(f"{current_time} Pass...")
    time.sleep(1)