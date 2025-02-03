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

def save_time(file_name):
    """'yyyy-mm-dd hh:mm:ss' 문자열 형식의 현재 시간을 txt 파일로 저장합니다. 

    :param file_name: 저장할 파일 이름
    :return: None
    """
    now = datetime.now()
    formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
    with open(file_name, "w") as file:
        file.write(formatted_time)

def load_time(file_name):
    """txt 파일에 저장된 'yyyy-mm-dd hh:mm:ss' 문자열 형식의 시간을 불러옵니다. 

    :param file_name: 불러올 파일 이름
    :return: <class 'datetime.datetime'>
    """
    with open(file_name, "r") as file:
        content = file.read()
        formatted_time = datetime.strptime(content, "%Y-%m-%d %H:%M:%S")
    return formatted_time