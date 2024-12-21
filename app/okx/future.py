# ----------------------------------------------
# # okx/future.py
#  * OKX 거래소 선물 거래 관련 모듈
#  * (주의!) 반드시 테스트 후 사용해야 합니다.
# ----------------------------------------------

import ccxt;
import os;
from dotenv import load_dotenv

load_dotenv()
OKX_API_KEY = os.environ.get("OKX_API_KEY")
OKX_API_SECRET_KEY = os.environ.get("OKX_API_SECRET_KEY")
OKX_API_PASSPHRASE = os.environ.get("OKX_API_PASSPHRASE")

okx = ccxt.okx({
    'apiKey': OKX_API_KEY,
    'secret': OKX_API_SECRET_KEY,
    'password': OKX_API_PASSPHRASE,
    'enableRateLimit': True,
})

def set_leverage(mode, symbol, leverage):
    """레버리지를 설정합니다.

    Args:
      - mode: 마진 모드(예: 교차인 경우 cross, 격리인 경우 isolated)
      - symbol: 가상화폐 종류(예: BTC-USDT-SWAP)
      - leverage: 레버리지 값(1 ~ 125) 
    
    Returns: <class 'dict'>
    """
    okx.set_margin_mode(mode, symbol, params={
        'lever': leverage,
    })

def create_market_order(symbol, trade_mode, order_side, amount, sl_price, tp_price):
    """시장가 주문을 체결합니다.

    Args:
      - symbol: 가상화폐 종류(예: BTC-USDT-SWAP)
      - trade_mode : 마진 모드(예: cross 또는 isolated)
      - order_side: 포지션 종류(예: 롱 주문은 buy, 숏 주문은 sell)
      - amount: 주문 수량(0.1이 최소 주문 수량이며, 0.1은 BTC 기준 0.001 BTC) 
      - sl_price: 손절(Stop Loss) 가격
      - tp_price: 수익실현(Take Profit) 가격
    
    Returns: <class 'dict'>
    """
    params={
        'tdMode': trade_mode,
        'stopLoss': {
            'type': 'market', 
            'triggerPrice': sl_price
        },
        'takeProfit': {
            'type': 'market',
            'triggerPrice': tp_price
        }
    }

    # 롱 포지션은 tp > sl, 숏 포지션은 sl > tp
    if(order_side=='buy' and tp_price > sl_price):
        order = okx.create_order(symbol, 'market', 'buy', amount, price=None, params=params)
        return order
    if(order_side=='sell' and sl_price > tp_price):
        order = okx.create_order(symbol, 'market', 'sell', amount, price=None, params=params)
        return order

    print(f'Stop Loss 가격과 Take Profit 가격이 적절한지 확인해주세요.')
    return None

def create_limit_order(symbol, trade_mode, order_side, amount, price, sl_price, tp_price):
    """지정가 주문을 체결합니다.

    Args:
      - symbol: 가상화폐 종류(예: BTC-USDT-SWAP)
      - trade_mode : 마진 모드(예: cross 또는 isolated)
      - order_side: 포지션 종류(예: 롱 주문은 buy, 숏 주문은 sell)
      - amount: 주문 수량(0.1이 최소 주문 수량이며, 0.1은 BTC 기준 0.001 BTC) 
      - price: 주문 가격
      - sl_price: 손절(Stop Loss) 가격
      - tp_price: 수익실현(Take Profit) 가격
    
    Returns: <class 'dict'>
    """
    params={
        'tdMode': trade_mode, 
        'stopLoss': {
            'type': 'market', 
            'triggerPrice': sl_price
        },
        'takeProfit': {
            'type': 'market',
            'triggerPrice': tp_price
        }
    }

    # 롱 포지션은 tp > price > sl, 숏 포지션은 sl > price > tp
    if(order_side=='buy' and tp_price > price > sl_price):
        order = okx.create_order(symbol, 'limit', 'buy', amount, price, params=params)
        return order
    if(order_side=='sell' and sl_price > price > tp_price):
        order = okx.create_order(symbol, 'limit', 'sell', amount, price, params=params)
        return order
    
    print(f'Stop Loss 가격과 Take Profit 가격이 적절한지 확인해주세요.')
    return None
