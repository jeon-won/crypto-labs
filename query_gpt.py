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
LIMIT = 200             ## 가져올 캔들 개수
MULTIPLIER = 3          ## 거래량, 캔들크기가 평균 대비 몇 배 이상일 떄 OpenAI에 질의할 것인지?

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
avg_vol_15 = oa.get_avg_vol_15ume(ohlcv_15m)
avg_candle_size_15m = oa.get_avg_candle_size_15m(ohlcv_15m)

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
        HumanMessage(content=f"""당신은 비트코인 단타로 수익을 내는 투자자입니다. 현재 거래량 또는 캔들 크기가 평균 대비 {MULTIPLIER}배 터졌거나 RSI 값이 과매수 또는 과매도 구간이기 때문에 질의합니다. 현재 롱 또는 숏 포지션을 잡으면 반드시 단타로 수익을 낼 수 있는지, 아니면 포지션을 잡지 않아야 하는지 판단해주세요.
        """),
        AIMessage(content=f"""비트코인 가격 정보 데이터입니다.
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
