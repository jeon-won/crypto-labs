import ccxt

binance = ccxt.binance(config={
    'options': {
        'defaultType': 'future'
    }
})

ohlcv = binance.fetch_ohlcv("BTC/USDT", "1m", limit=100)
print(ohlcv)