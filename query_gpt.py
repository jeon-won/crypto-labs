import api.ohlcv_analyzer as oa
import ccxt
import os
from api.messenger import send_discord_message
from dotenv import load_dotenv
from langchain_openai.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage

# 상수
load_dotenv()
DISCORD_WEBHOOK_URL = os.environ.get('DISCORD_WEBHOOK_URL')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
MODEL_NAME = "o1-mini"  ## 사용 가능한 모델 이름은 https://platform.openai.com/docs/models 의 Current model aliases 참고
SYMBOL = 'BTC/USDT'
LIMIT = 100             ## 가져올 캔들 개수
MULTIPLIER = 3          ## 거래량, 캔들크기가 평균 대비 몇 배 이상일 떄 OpenAI에 질의할 것인지?

human_message = f"""당신은 비트코인 단타 투자자입니다. 아래 기준에 따라 지금 롱 또는 숏 포지션을 잡으면 수익 실현이 가능한지, 아니면 포지션을 잡지 말아야 하는지 판단해주세요. 

```markdown
# 공통사항
* 현재 캔들이 앞전 캔들들 대비 거래량이 월등히(5배 이상) 많으면서 봉 길이가 아주 길거나 아주 짧으면 좋음
* 5분봉이 좋아보여도 15분봉이 좋지 않으면 포지션을 잡지 않음

# 다음 조건 중 적어도 2개 이상을 만족하면 수익 실현이 가능하다고 봄
1. 현재 캔들 크기와 거래량이 평균 대비 5배 이상 큰 경우
2. 현재 3틱 패턴인 경우
  - 양봉에서 음봉으로 전환된 캔들은 1틱으로 인정하지 않음. 단 이전 캔들보다 월등히 큰 경우 1틱으로 인정
  - 이전 1틱과 크기가 비슷한 캔들을 묶어 2틱으로 인정
  - 중간에 추세를 깨지않을 만큼의 양봉이 뜨면 한데 묶어 1틱으로 인정. 단 30% 이상 상승했다면 지금까지 인정한 틱을 초기화함.
  - 이렇게 3틱이 완성되면 3틱 패턴인 걸로 인정함
3. 현재 찐바닥 패턴인 경우
  - 캔들의 길이가 점점 짧아짐
  - 아래(위)꼬리 캔들이 생성되기 시작함
  - 이전 캔들의 종가와 현재 캔들의 종가가 거의 차이나지 않음
4. 현재 다이버전스 발생
  - 상승 다이버전스 발생: 현재 종가와 거래량이 직전 저점의 종가와 거래량보다 낮은 경우
  - 하락 다이버전스 발생: 현재 종가가 직전 고점의 종가보다 높고, 현재 거래량이 직전 고점의 거래량보다 낮은 경우
5. 현재 캔들이 지지선, 저항선, 채널, 추세선 또는 피보나치 구간에 위치한 경우
```

아래 Markdown 형식으로 답해주세요.
```markdown
# 비트코인 포지션 판단
* 결정: 
* 이유: 
```
"""

# 비트코인 두 캔들의 ohlcv 값 가져오기
binance = ccxt.binance(config={
    'options': {
        'defaultType': 'future'
    }
})
ohlcv_15m = binance.fetch_ohlcv(SYMBOL, '15m', limit=LIMIT)
ohlcv_5m = binance.fetch_ohlcv(SYMBOL, '5m', limit=LIMIT)

# 여러 데이터 저장
## 현재 거래량, 캔들크기 및 RSI 값 저장
current_vol_15m = ohlcv_15m[-1][5]
current_vol_5m = ohlcv_5m[-1][5]
current_candle_size_15m = abs(((ohlcv_15m[-1][4] - ohlcv_15m[-1][1]) / ohlcv_15m[-1][1]) * 100)
current_candle_size_5m = abs(((ohlcv_5m[-1][4] - ohlcv_5m[-1][1]) / ohlcv_5m[-1][1]) * 100)
current_rsi_15m = oa.calculate_rsi(ohlcv_15m)
current_rsi_5m = oa.calculate_rsi(ohlcv_5m)
## 평균 거래량 및 캔들크기 저장
avg_vol_15 = oa.get_avg_volume(ohlcv_15m)
avg_candle_size_15m = oa.get_avg_candle_size(ohlcv_15m)

# OpenAI에 질의할 타이밍이면 질의
is_timing = (current_vol_15m >= avg_vol_15 * MULTIPLIER) or \
    (current_candle_size_15m >= avg_candle_size_15m * MULTIPLIER) or \
    (current_rsi_15m <= 30 or current_rsi_15m >= 70)
if(is_timing):
    chat = ChatOpenAI(
        openai_api_key=OPENAI_API_KEY,
        model_name=MODEL_NAME,
        temperature=1.0,
    )
    messages = [
        HumanMessage(content=human_message),
        AIMessage(content=f"""비트코인 가격 정보 데이터
        * 현재 RSI: 15분봉 {current_rsi_15m}, 5분봉 {current_rsi_5m}
        * OHLCV 데이터
            - 15분봉 {ohlcv_15m}
            - 5분봉: {ohlcv_5m}
            - 각 배열의 0번째 요소는 Unixtime, 1번째 요소는 시가, 2번째 요소는 고가, 3번째 요소는 저가, 4번째 요소는 종가, 5번째 요소는 거래량임
        """),
    ]

    # OpenAI 질의 결과를 Discord 메시지 전송
    response = chat.invoke(messages)
    send_discord_message(DISCORD_WEBHOOK_URL, response.content)
