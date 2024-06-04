# crypto-labs

가상화폐 거래 연구용(?) 리포지토리 입니다.


## 환경변수

일부 코드에서 API 키를 사용할 수 있습니다.

```python
OKX_API_KEY="oKxApIkEy"
OKX_API_SECRET_KEY="oKxApIsEcReTkEy"
OKX_API_PASSPHRASE="oKxApIpAsSpHrAsE"

FLASK_PORT=8000
```


## okx

### future.py

OKX 거래소 선물 거래 관련 모듈. OKX 거래소 API 키가 필요하며, 아래 함수들을 사용합니다.

* `set_leverage()`: 레버리지 설정
* `create_market_order()`: 시장가 주문 체결
* `create_limit_order()`: 지정가 주문 체결

### webhook.py

Flask 서버를 사용하여 트레이딩뷰 웹훅 메시지를 받아 처리하는 코드(작성 중)