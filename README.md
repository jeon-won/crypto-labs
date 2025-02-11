# crypto-labs

가상화폐 거래 연구용(?) 리포지토리 입니다.

테스트 중인 코드이므로 정상적인 실행을 보장하지 않으며, 이 프로그램을 사용하여 발생하는 손해에 대한 책임은 사용자 본인에게 있습니다.


## 환경변수

일부 코드에서 API 키를 사용할 수 있습니다. 루트 경로에 `.env` 파일을 만든 후 아래와 같이 작성하여 사용하면 됩니다.

```python
DISCORD_WEBHOOK_URL="https://discord.com/api/hooks/dIsC0RdHo0KuRl"

TELEGRAM_TOKEN="1234567890:tElEgRaMtOkEn"
TELEGRAM_CHAT_ID="2345678901"

OKX_API_KEY="oKxApIkEy"
OKX_API_SECRET_KEY="oKxApIsEcReTkEy"
OKX_API_PASSPHRASE="oKxApIpAsSpHrAsE"

OPENAI_API_KEY="oPeNaPiKeY"
```

## 디렉터리 구조

### 최상위 경로

`query-gpt.py`는 OpenAI API를 사용하여 차트 분석을 맡기는 코드.

`o3-mini.py`는 OpenAI o3-mini API를 사용하여 질의하는 테스트 코드. Tier 3 됐는데도 작동이 안 됨... 😭

### api

`common.py`는 공통 기능을 모아놓을 예정인(?) 모듈.

  * `convert_unixtime_to_datetime()`: Unixtime(10자리 또는 13자리 숫자)을 'yyyy-mm-dd hh:mm:ss' 문자열로 변환
  * `save_time()`: yyyy-mm-dd hh:mm:ss' 문자열 형식의 현재 시간을 txt 파일로 저장
  * `load_time()`: txt 파일에 저장된 'yyyy-mm-dd hh:mm:ss' 문자열 형식의 시간을 불러옴

`divergence.py`는 o3-mini-high를 사용하여 만들어 본 코드. 테스트 안 해봄...

`messenger.py`는 메시지를 보내는 모듈.

  * `send_telegram_message()`: 텔레그램 메시지 전송
  * `send_discord_message()`: 디스코드 웹훅 메시지 전송

`ohlcv_analyzer_v1.py`는 OHLCV(open, high, low, close, volume) 데이터를 분석하는 모듈. OHLCV 데이터는 ccxt 라이브러리의 `fetch_ohlcv()` 함수가 반환합니다.

  * `get_avg_candle_size()`: 평균 캔들 크기 계산
  * `get_avg_volume()`: 평균 거래량 계산
  * `is_three_tick()`: 3틱 캔들 생성 여부 확인
  * `is_tail_candles()`: 일정 개수의 꼬리 캔들 생성 여부 확인
  * `is_big_candle_size()`: 겁나 큰 캔들인지 확인
  * `is_big_volume()`: 거래량 터졌는지 확인
  * `calculate_rsi()`: RSI 값 계산. 반드시 fetch_ohlcv() 함수의 limit 파라미터 값을 200으로 설정하여 반환한 값을 사용해야 함.

### archive

잉여 코드 보관소

### chartview

멀티 차트를 보여주는 HTML

### mongodb

* `docker-compose.yaml`: MongoDB 8.0.0 버전 컨테이너를 만드는 Docker Compose YAML 파일
* `mongodb_test.py`: MongoDB에 OHLCV 데이터를 시험삼아 저장해보는 코드

### okx

OKX 거래소 관련 코드

`future.py`는 OKX 거래소 선물 거래 관련 모듈. 환경변수에 OKX 거래소 API 키를 등록해야 함.

* `set_leverage()`: 레버리지 설정
* `create_market_order()`: 시장가 주문 체결
* `create_limit_order()`: 지정가 주문 체결

`webhook.py`는 Flask 서버를 사용하여 트레이딩뷰 웹훅 메시지를 받아 처리하는 코드(작성 중이었지만 포기함...)