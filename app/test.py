TIMEFRAME = ["3m", "5m", "15m", "1h", "2h", "4h"]

def check_timeframe(timeframe):
    # 5분봉과 15분봉이 같이 있으면 True
    if "5m" in timeframe and "15m" in timeframe:
        return True
    # 15분봉이 있으면서 그 이상 봉 중 하나라도 있으면 True
    if "15m" in timeframe and any(t in timeframe for t in ["1h", "2h", "4h"]):
        return True
    return False

print(check_timeframe(["15m", "5m", "13h"]))