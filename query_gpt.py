import api.ohlcv_analyzer as oa
import ccxt
import os
import openai
from api.messenger import send_discord_message
from dotenv import load_dotenv

# 상수
load_dotenv()
DISCORD_WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
MODEL_NAME = "o1-mini"  ## gpt-4o, gpt-4o-mini, o1-mini 등
SYMBOL = 'BTC/USDT'
LIMIT = 150             ## 가져올 캔들 개수
MULTIPLIER = 3          ## 거래량, 캔들크기가 평균 대비 몇 배 이상일 떄 OpenAI에 질의할 것인지?

# 비트코인 두 캔들의 ohlcv 값 가져오기
binance = ccxt.binance(config={
    'options': {
        'defaultType': 'future'
    }
})

ohlcv_15m = binance.fetch_ohlcv(SYMBOL, '15m', limit=LIMIT)
current_price = ohlcv_15m[-1][4]
transformed_ohlcv_15m = []

# 입력 토큰 절약을 위해 Unixtime 자릿수 절감 및 그 외 데이터 반올림
for row in ohlcv_15m:
    timestamp = row[0] // 1000                         ## 첫 번째 요소는 뒤 0 3개를 제거
    values = [round(value) for value in row[1:]]       ## 나머지 요소는 소수값을 반올림하여 자연수로 변경
    transformed_ohlcv_15m.append([timestamp] + values) ## 변환된 데이터를 새로운 리스트에 추가

print(f"현재가: {current_price}")

# 여러 데이터 저장
## 현재 거래량, 캔들크기 및 RSI 값 저장
current_vol_15m = ohlcv_15m[-1][5]
current_candle_size_15m = abs(((ohlcv_15m[-1][4] - ohlcv_15m[-1][1]) / ohlcv_15m[-1][1]) * 100)
current_rsi_15m = oa.calculate_rsi(ohlcv_15m)
## 평균 거래량 및 캔들크기 저장
avg_vol_15 = oa.get_avg_volume(ohlcv_15m)
avg_candle_size_15m = oa.get_avg_candle_size(ohlcv_15m)

prompt = f"""당신은 비트코인이 상승 또는 하락 추세로 전환하기 직전에 포지션을 잡아 수익을 내야 합니다. 예를 들어 하락에서 상승으로 전환하기 직전에 롱 포지션을, 상승에서 하락으로 전환하기 직전에 숏 포지션을 잡은 후 1시간 내로 포지션을 정리하여 수익을 내야 합니다.

OHLCV 데이터를 참고하여 비트코인 포지션을 잡아도 되는지 판단해주세요. 비트코인 데이터는 다음과 같습니다.
* 현재 가격: 
* 현재 RSI: {current_rsi_15m}
* OHLCV 데이터: {transformed_ohlcv_15m}
  - OHLCV 데이터 각 배열의 0번째 요소는 Unixtime, 1번째 요소는 시가, 2번째 요소는 고가, 3번째 요소는 저가, 4번째 요소는 종가, 5번째 요소는 거래량임
  - 위의 3가지 OHLCV 캔들 데이터를 분석하여 제시한 조건들 중 적어도 2가지 이상 만족하는지 판단해야 함
* 캔들 관련 값 계산 방법
  - 현재 캔들이란 OHLCV 데이터의 Unixtime 값이 가장 최신인 캔들을 가리킴
  - 양봉 캔들: `종가 > 시가`
  - 음봉 캔들: `시가 > 종가`
  - 캔들 크기 = `|시가 - 종가|`
  - 캔들의 아래꼬리 길이 = 양봉인 경우 `시가 - 저가`, 음봉인 경우 `종가 - 저가`
  - 캔들의 위꼬리 길이 = 양봉인 경우 `고가 - 종가`, 음봉인 경우 `고가 - 시가`

아래 기준을 적어도 2개 이상 만족한다면 수익이 발생한다고 가정합니다.
1. 현재 캔들 크기와 거래량이 평균 대비 3배 이상 큰 경우
2. 현재 캔들이 3틱 패턴인 경우(다음과 같이 추측해야 함)
  - 양봉에서 음봉으로 전환된 캔들은 1틱으로 인정하지 않음. 단 이전 캔들보다 월등히 큰 경우 1틱으로 인정
  - 이전 1틱과 크기가 비슷한 캔들을 묶어 2틱으로 인정
  - 중간에 추세를 깨지않을 만큼의 양봉이 뜨면 한데 묶어 1틱으로 인정. 단 30% 이상 상승했다면 지금까지 인정한 틱을 초기화함.
  - 이렇게 현재 캔들이 포함된 3틱이 완성되면 3틱 패턴인 걸로 인정함
3. 현재 캔들이 찐바닥 패턴인 경우(다음과 같이 추측해야 함)
  - 캔들의 길이가 점점 짧아짐
  - 아래 또는 위꼬리 캔들이 생성되기 시작함
  - 이전 캔들의 종가와 현재 캔들의 종가가 거의 차이나지 않음
4. 현재 캔들에 다이버전스가 발생한 경우(아래와 같이 추측해야 함)
  - 상승 다이버전스 발생: 현재 종가가 직전 저점의 종가보다 낮고 현재 거래량이 직전 저점의 거래량보다 낮은 경우
  - 하락 다이버전스 발생: 현재 종가가 직전 고점의 종가보다 높고 현재 거래량이 직전 고점의 거래량보다 낮은 경우
5. 지지선, 저항선, 채널, 추세선 또는 피보나치 구간이 어딘지 추측한 후, 현재 캔들이 여기에 위치한 경우
6. 이 외에 수익을 낼 수 있을 신호가 발생한 경우

아래 Markdown 형식으로 답해주세요.
# 비트코인 포지션 판단
* 결정: (롱, 숏 또는 관망 중 하나로 결정)
* 이유: (판단 근거)
* 예상 수익실현 가격: (롱, 숏 포지션인 경우 명시)
* 예상 손절 가격: (롱, 숏 포지션인 경우 명시)
"""

# OpenAI에 질의할 타이밍이면 질의
is_timing = (current_vol_15m >= avg_vol_15 * MULTIPLIER) or \
    (current_candle_size_15m >= avg_candle_size_15m * MULTIPLIER) or \
    (current_rsi_15m <= 30 or current_rsi_15m >= 70)
if(True):
    response = openai.chat.completions.create(
        model=MODEL_NAME,  # 사용할 모델
        messages=[
            # {"role": "system", "content": "당신은 비트코인 단타 투자 전문가입니다."},  # 시스템 메시지. o1-mini에선 사용 안 함.
            {"role": "user", "content": prompt},  # 사용자 입력
        ],
        # max_tokens=150,  # 최대 토큰 수
        # temperature=0,  # 응답의 창의성 정도. o1-mini는 1만 사용 가능.
    )
    # 응답 출력
    print(response.choices[0].message.content)
    send_discord_message(DISCORD_WEBHOOK_URL, response.choices[0].message.content)
