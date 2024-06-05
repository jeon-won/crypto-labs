# crypto-labs

가상화폐 거래 연구용(?) 리포지토리 입니다.


## 환경변수

일부 코드에서 API 키를 사용할 수 있습니다.

```python
FLASK_PORT=8000
DISCORD_WEBHOOK_URL="https://discord.com/api/hooks/dIsC0RdHo0KuRl

OKX_API_KEY="oKxApIkEy"
OKX_API_SECRET_KEY="oKxApIsEcReTkEy"
OKX_API_PASSPHRASE="oKxApIpAsSpHrAsE"

```


## discord

### discord.py

디스코드 메시지를 보내는 모듈. 환경변수에 디스코드 채팅 채널 웹훅 주소를 등록해야 합니다.

* `send_discord_message()`: 웹훅을 사용하여 디스코드 채팅 채널에 메시지 전송


## okx

### future.py

OKX 거래소 선물 거래 관련 모듈. 환경변수에 OKX 거래소 API 키를 등록해야 합니다.

* `set_leverage()`: 레버리지 설정
* `create_market_order()`: 시장가 주문 체결
* `create_limit_order()`: 지정가 주문 체결

### webhook.py

Flask 서버를 사용하여 트레이딩뷰 웹훅 메시지를 받아 처리하는 코드(작성 중)