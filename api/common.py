from datetime import datetime

def convert_unixtime_to_datetime(unixtime):
    """Unixtime을 'yyyy-mm-dd hh:mm:ss' 문자열로 변환합니다.

    :param unixtime: 10자리 또는 13자리의 Unixtime
    :return: 'yyyy-mm-dd hh:mm:ss' 문자열 <class 'str'>
    """
    # 13자리 유닉스 타임인 경우 밀리초 단위이므로 1000으로 나눔
    if len(str(unixtime)) == 13:
        unixtime = unixtime / 1000
    
    # 유닉스 타임을 datetime 객체로 변환 및 반환
    dt = datetime.fromtimestamp(unixtime)
    return dt.strftime('%Y-%m-%d %H:%M:%S')