import pandas as pd

"""ohlcv_analyzer.py
ccxt의 fetch_ohlcv() 함수가 반환하는 배열 데이터를 지지고 볶는(?) 모듈입니다.
"""

def count_doji_candles(ohlcv):
    """도지 캔들 개수를 반환합니다.

    :param ohlcv: ccxt의 fetch_ohlcv() 함수가 반환하는 2차원 배열
    """
    count = 0

    # 몸통이 전체 범위에 비해 매우 작은 경우(10% 미만) 도지 캔들로 판단
    for item in ohlcv:
        candle_lange = item[2] - item[3]
        body = abs(item[4] - item[1])
        if(candle_lange > 0 and (body / candle_lange) < 0.1):
            count += 1
    
    return count


def count_hammer_candles(ohlcv):
    """망치형(아래꼬리) 캔들 개수를 반환합니다.

    :param ohlcv: ccxt의 fetch_ohlcv() 함수가 반환하는 2차원 배열
    """
    count = 0
    # 아래꼬리가 몸통의 2배 이상인 경우 망치형 캔들로 판단
    for item in ohlcv:
        body = abs(item[4] - item[1])    ## 몸통 크기
        candle_range = item[2] - item[3] ## 캔들범위
        upper_shadow = item[2] - max(item[1], item[4]) ## 위꼬리 크기: 양봉일 경우 high - close, 음봉일 경우 high - open
        lower_shadow = min(item[1], item[4]) - item[3] ## 아래꼬리 크기: 양봉일 경우 open - low, 음봉일 경우 close - low
        if((body < candle_range * 0.1) and \
           (lower_shadow >= body * 2)) and \
           (upper_shadow >= body * 0.5):
            count += 1
    
    return count

def count_inverted_hammer_candles(ohlcv):
    """역망치형(아래꼬리) 캔들 개수를 반환합니다.

    :param ohlcv: ccxt의 fetch_ohlcv() 함수가 반환하는 2차원 배열
    """
    count = 0
    # 아래꼬리가 몸통의 2배 이상인 경우 망치형 캔들로 판단
    for item in ohlcv:
        body = abs(item[4] - item[1])    ## 몸통 크기
        candle_range = item[2] - item[3] ## 캔들범위
        upper_shadow = item[2] - max(item[1], item[4]) ## 위꼬리 크기: 양봉일 경우 high - close, 음봉일 경우 high - open
        lower_shadow = min(item[1], item[4]) - item[3] ## 아래꼬리 크기: 양봉일 경우 open - low, 음봉일 경우 close - low
        if((body < candle_range * 0.1) and \
           (upper_shadow >= body * 2)) and \
           (lower_shadow >= body * 0.5):
            count += 1
    
    return count