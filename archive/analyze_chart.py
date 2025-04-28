import api.ohlcv_analyzer_v2 as oa
from api.common import save_time, load_time
import ccxt
import os
import openai
from api.messenger import send_discord_message
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
SYMBOL = 'BTC/USDT'
TIMEFRAME_1 = '15m'
TIMEFRAME_2 = '5m'
LIMIT = 200

binance = ccxt.binance(config={
    'options': {
        'defaultType': 'future'
    }
})
tf_1_ohlcv = binance.fetch_ohlcv(SYMBOL, TIMEFRAME_1, limit=LIMIT)
tf_2_ohlcv = binance.fetch_ohlcv(SYMBOL, TIMEFRAME_2, limit=LIMIT)

# 알림 조건
## RSI 값이 과매수 또는 과매도
tf_1_rsi = oa.calculate_rsi(tf_1_ohlcv)
tf_2_rsi = oa.calculate_rsi(tf_2_ohlcv)

## 현재 거래량이 평균 대비 3배 이상인 경우
tf_1_vol = oa.get_avg_volume(tf_1_ohlcv)
tf_2_vol = oa.get_avg_volume(tf_2_ohlcv)

## 현재 캔들 크기가 평균 대비 3대 이상인 경우
tf_1_candle_size = oa.get_avg_candle_size(tf_1_ohlcv)
tf_2_candle_size = oa.get_avg_candle_size(tf_2_ohlcv)

## (역)망치형 캔들이 여럿 있는 경우
tf_1_hammer_count = oa.count_hammer_candles(tf_1_ohlcv)
tf_1_inverted_hammer_count = oa.count_inverted_hammer_candles(tf_1_ohlcv)
tf_2_hammer_count = oa.count_hammer_candles(tf_2_ohlcv)
tf_2_inverted_hammer_count = oa.count_inverted_hammer_candles(tf_2_ohlcv)

## 현재 캔들이 거래량 짱짱 터진 도지 캔들인 경우