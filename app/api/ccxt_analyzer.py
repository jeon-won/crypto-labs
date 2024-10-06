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
    """3틱 캔들이 생성됐는지 확인합니다.

    :param ohlcv: ccxt의 fetch_ohlcv() 함수가 반환하는 배열
    :param std_size: 3틱 캔들 판별을 위한 캔들 크기 기준. 단위는 %. (이 크기보다 큰 캔들은 1틱으로 간주)
    :return: 3틱룰에 부합하면 true, 아니면 false
    """
    # 변수
    count_tick = 0  ## 틱 

    # 각 캔들을 분석하여 틱 생성 확인
    for item in ohlcv:
        candle_size = abs(((item[4] - item[1]) / item[1]) * 100)
        if(candle_size >= std_size):
            count_tick += 1
    
    # 3틱룰 여부 반환
    if(count_tick >= 3):
        return True
    return False


def is_tail_candles(ohlcv, std_ratio, std_num):
    """일정 개수의 꼬리 캔들이 생성되었는지 확인합니다.

    :param ohlcv: ccxt의 fetch_ohlcv() 함수가 반환하는 배열
    :param std_ratio: 꼬리:몸통 비율(예: std_ratio 값이 2면 꼬리:몸통 비율은 2:1)
    :param std_num: 꼬리 캔들이 몇개 생성되었는가?
    :return: 조건에 부합하면 true, 아니면 false
    """

    # 변수
    number_of_candles = 0 ## 꼬리 캔들 개수

    # 각 캔들의 몸통과 꼬리 크기 계산
    for item in ohlcv:
        ## for 문에서 사용하는 변수
        candle_body = 0.0       ### 캔들 몸통 크기
        tail_upper = 0.0        ### 위꼬리 크기
        tail_bottom = 0.0       ### 아래꼬리 크기
        ratio_tail_upper = 0.0  ### 위꼬리:몸통 비율
        ratio_tail_bottom = 0.0 ### 아래꼬리:몸통 비율

        ## 양봉인 경우(종가 > 시가)
        if(item[4] > item[1]):
            candle_body = item[4] - item[1]  ### 몸통 크기 = 종가 - 시가
            tail_upper = item[2] - item[4]   ### 위꼬리 크기 = 고가 - 종가
            tail_bottom = item[1] - item[3]  ### 아래꼬기 크기 = 시가 - 저가

        ## 음봉인 경우(시가 > 종가)
        if(item[1] > item[4]):
            candle_body = item[1] - item[4]  ### 몸통 크기 = 시가 - 종가
            tail_upper = item[2] - item[1]   ### 위꼬리 크기 = 고가 - 시가
            tail_bottom = item[4] - item[3]  ### 아래꼬리 크기 = 종가 - 저가
        
        ## 꼬리:몸통 비율이 일정 크기 이상이면 꼬리 캔들 개수 추가
        ratio_tail_upper = tail_upper / candle_body
        ratio_tail_bottom = tail_bottom / candle_body
        if(ratio_tail_upper >= std_ratio or ratio_tail_bottom >= std_ratio):
            number_of_candles += 1
    
    # 꼬리 캔들이 일정 개수 이상 생성되었다면 True 반환
    if(number_of_candles >= std_num):
        return True
    return False


def is_big_candle_size(ohlcv_item, std_size, multiple):
    """겁나 큰 캔들인지 판별합니다.

    :param ohlcv_item: ccxt의 fetch_ohlcv() 함수가 반환하는 배열 요소 1개
    :param std_size: 캔들 크기 기준
    :param multiple: 배수
    :return: 캔들이 std_size의 multiple배 크기 이상이면 True, 아니면 False
    """
    # 캔들 크기가 std_size의 multiple배 이상이면 True 반환
    candle_size = abs(ohlcv_item[1] - ohlcv_item[4])
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