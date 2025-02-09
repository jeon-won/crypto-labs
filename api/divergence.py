"""
o3-mini-high를 사용하여 만들어본 Bullish divergence, Bearish divergence 판별 함수(테스트 필요)
"""

def find_last_swing_low(candles):
    """
    candles 리스트에서 (현재 캔들을 제외하고) 양쪽 이웃보다 낮은
    마지막 스윙 저점을 찾습니다.
    """
    # 최소 3개의 캔들이 있어야 판단할 수 있음
    for i in range(len(candles) - 2, 0, -1):
        # candles[i][3] 는 저점 (low)
        if candles[i][3] < candles[i-1][3] and candles[i][3] < candles[i+1][3]:
            return candles[i]
    return None

def find_last_swing_high(candles):
    """
    candles 리스트에서 (현재 캔들을 제외하고) 양쪽 이웃보다 높은
    마지막 스윙 고점을 찾습니다.
    """
    for i in range(len(candles) - 2, 0, -1):
        # candles[i][2] 는 고점 (high)
        if candles[i][2] > candles[i-1][2] and candles[i][2] > candles[i+1][2]:
            return candles[i]
    return None

def detect_divergence(candles):
    """
    주어진 캔들 데이터에서 현재 캔들에 대해 bullish divergence와 bearish divergence를 확인합니다.
    
    조건:
      - Bullish Divergence: 
            현재 캔들의 저점 (index 3)이 마지막 스윙 저점보다 낮고,
            RSI (index 6)는 마지막 스윙 저점의 RSI보다 높으면 bullish divergence.
      
      - Bearish Divergence: 
            현재 캔들의 고점 (index 2)이 마지막 스윙 고점보다 높고,
            RSI (index 6)는 마지막 스윙 고점의 RSI보다 낮으면 bearish divergence.
    
    캔들 하나의 형식: [unixtime, open, high, low, close, volume, rsi]
    
    Returns:
        (bullish_divergence, bearish_divergence)  -> 두 boolean 값
    """
    if len(candles) < 3:
        # 데이터가 부족하면 판단할 수 없음
        return False, False

    current = candles[-1]
    # 현재 캔들을 제외한 데이터에서 스윙 포인트를 찾음
    historical = candles[:-1]

    bullish_div = False
    bearish_div = False

    # Bullish divergence 판별
    pivot_low = find_last_swing_low(historical)
    if pivot_low is not None:
        # 조건: 현재 캔들의 low가 pivot_low의 low보다 낮고, 현재 RSI가 pivot_low의 RSI보다 높을 때
        if current[3] < pivot_low[3] and current[6] > pivot_low[6]:
            bullish_div = True

    # Bearish divergence 판별
    pivot_high = find_last_swing_high(historical)
    if pivot_high is not None:
        # 조건: 현재 캔들의 high가 pivot_high의 high보다 높고, 현재 RSI가 pivot_high의 RSI보다 낮을 때
        if current[2] > pivot_high[2] and current[6] < pivot_high[6]:
            bearish_div = True

    return bullish_div, bearish_div

# 예시 사용법:
if __name__ == '__main__':
    # 예시 데이터 (실제 데이터는 더 길게 들어올 것입니다)
    candles = [
        [1617184800, 58000, 58500, 57700, 58400, 12.5, 45.0],
        [1617188400, 58400, 58600, 58300, 58550, 10.2, 44.5],
        [1617192000, 58550, 58700, 58450, 58600, 11.0, 43.0],
        # ... (더 많은 캔들 데이터)
        [1617210000, 58000, 58200, 57800, 58100, 13.0, 47.5]  # 현재 캔들
    ]
    
    bullish, bearish = detect_divergence(candles)
    print("Bullish Divergence:", bullish)
    print("Bearish Divergence:", bearish)