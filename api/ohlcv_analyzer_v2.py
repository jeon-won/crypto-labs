import pandas as pd

"""ohlcv_analyzer_v2.py
ccxt의 fetch_ohlcv() 함수가 반환하는 배열 데이터를 지지고 볶는(?) 모듈입니다.
"""

def get_avg_candle_size(ohlcv):
    """평균 캔들 크기를 계산합니다.

    :param ohlcv: ccxt의 fetch_ohlcv() 함수가 반환하는 배열
    :return: 평균 캔들 크기. 단위는 % <class 'float'>
    """
    # 변수
    sum_candle_size = 0            ## 모든 캔들 사이즈의 합
    avg_candle_size = 0            ## 캔들 사이즈의 평균
    number_of_candles = len(ohlcv) ## 캔들 개수

    # 각 캔들의 크기를 계산하여 합함
    for item in ohlcv:
        ## 캔들 크기 계산식 = |[(종가 - 시가) / 시가] * 100|
        candle_size = abs(((item[4] - item[1]) / item[1]) * 100)
        sum_candle_size += candle_size
    
    # 캔들 사이즈의 평균 값 반환
    avg_candle_size = round(sum_candle_size / number_of_candles, 3)
    return avg_candle_size


def get_avg_volume(ohlcv):
    """평균 거래량을 계산합니다
    
    :param ohlcv: ccxt의 fetch_ohlcv() 함수가 반환하는 배열
    :return: 평균 거래량 <class 'float'>
    """
    # 변수
    sum_volume = 0                 ## 모든 캔들 거래량의 합
    avg_volume = 0                 ## 거래량 평균
    number_of_candles = len(ohlcv) ## 캔들 개수

    # 각 캔들의 거래량을 합함
    for item in ohlcv:
        sum_volume += item[5]
    
    # 거래량 평균 반환
    avg_volume = int(round(sum_volume / number_of_candles, 0))
    return avg_volume


def is_three_tick(ohlcv, std_size):
    """양봉3틱 또는 음봉3틱 캔들이 생성됐는지 확인합니다.

    :param ohlcv: ccxt의 fetch_ohlcv() 함수가 반환하는 배열
    :param std_size: 3틱 캔들 판별을 위한 기준 크기. 단위는 %. (이 크기보다 큰 캔들은 1틱으로 간주)
    :return: 3틱룰에 부합하면 true, 아니면 false
    """

    # 대충 std_size 크기 이상의 양봉, 음봉 캔들이 3개 이상 생긴 경우 True를 반환하면 될 듯

    # 변수: 양봉 틱과 음봉 틱 개수
    count_yang = 0
    count_eum = 0

    # 각 캔들을 분석하여 틱 생성 확인
    for item in ohlcv:
        candle_size = abs(((item[4] - item[1]) / item[1]) * 100)
        if(candle_size >= std_size): ## 캔들 크기가 기준 크기보다 크면 1틱으로 간주
            if(item[4] > item[1]):   ### 양봉 1틱
                count_yang += 1
            if(item[1] > item[4]):   ### 음봉 1틱
                count_eum += 1
    
    # 양봉3틱 또는 음봉3틱 여부 반환
    if(count_yang >= 3 or count_eum >= 3):
        return True
    return False


def is_big_candle_size(ohlcv_item, std_size, multiple):
    """겁나 큰 캔들인지 판별합니다.

    :param ohlcv_item: ccxt의 fetch_ohlcv() 함수가 반환하는 배열 요소 1개
    :param std_size: 캔들 크기 기준(단위: %)
    :param multiple: 배수
    :return: 캔들이 std_size의 multiple배 크기 이상이면 True, 아니면 False
    """
    # 캔들 크기가 std_size의 multiple배 이상이면 True 반환
    candle_size = abs(((ohlcv_item[4] - ohlcv_item[1]) / ohlcv_item[1]) * 100)
    if(candle_size >= std_size * multiple):
        return True
    return False


def is_big_volume(ohlcv_item, std_vol, multiple):
    """거래량이 일정 수준 이상인지 판별합니다.

    :param ohlcv_item: ccxt의 fetch_ohlcv() 함수가 반환하는 배열 요소 1개
    :param std_vol: 거래량 기준
    :param multiple: 배수
    :return: 거래량이 std_vol의 multiple배 크기 이상이면 True, 아니면 False
    """
    volume = ohlcv_item[5]
    if(volume >= std_vol * multiple):
        return True
    return False


def calculate_rsi(ohlcv_list: list, period: int = 14):
    """
    ccxt의 fetch_ohlcv() 함수가 반환하는 list 객체를 받아 RSI 값을 계산합니다. (rsi_calc 함수를 통합함)
    
    Args: 
        - ohlcv_list: list (ccxt의 fetch_ohlcv() 함수의 반환값)
        - period: 이동평균 길이 (기본: 14)
    
    Returns: <class 'numpy.float64'>
    """
    # DataFrame으로 변환
    df = pd.DataFrame(ohlcv_list)
    ohlc = df[4].astype(float)  # 종가 데이터

    # RSI 계산
    delta = ohlc.diff()
    gains, declines = delta.copy(), delta.copy()
    gains[gains < 0] = 0
    declines[declines > 0] = 0

    _gain = gains.ewm(com=(period - 1), min_periods=period).mean()
    _loss = declines.abs().ewm(com=(period - 1), min_periods=period).mean()

    RS = _gain / _loss
    rsi = 100 - (100 / (1 + RS))
    
    return float(rsi.iloc[-1])


def count_doji_candles(ohlcv):
    """도지 캔들 개수를 반환합니다.

    :param ohlcv: ccxt의 fetch_ohlcv() 함수가 반환하는 2차원 배열
    """
    count = 0

    # 몸통이 전체 범위에 비해 매우 작은 경우(10% 이하) 도지 캔들로 판단
    for item in ohlcv:
        candle_lange = item[2] - item[3]
        body = abs(item[4] - item[1])
        if(candle_lange > 0 and (body / candle_lange) <= 0.1):
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
        candle_range = item[2] - item[3] ## 캔들 범위
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
        candle_range = item[2] - item[3] ## 캔들 범위
        upper_shadow = item[2] - max(item[1], item[4]) ## 위꼬리 크기: 양봉일 경우 high - close, 음봉일 경우 high - open
        lower_shadow = min(item[1], item[4]) - item[3] ## 아래꼬리 크기: 양봉일 경우 open - low, 음봉일 경우 close - low
        if((body < candle_range * 0.1) and \
           (upper_shadow >= body * 2)) and \
           (lower_shadow >= body * 0.5):
            count += 1
    
    return count