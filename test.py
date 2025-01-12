import ccxt
import api.ohlcv_analyzer as oa

binance = ccxt.binance(config={
    'options': {
        'defaultType': 'future'
    }
})

search = [
    ('5m', '5분봉'),
    ('15m', '15분봉'),
    ('1h', '1시간봉'),
    ('4h', '4시간봉'),
]

dict_rsi = {}
for item in search:
    ohlcv = binance.fetch_ohlcv('BTC/USDT', item[0], limit=200)
    rsi = oa.calculate_rsi(ohlcv)
    dict_rsi[item[0]] = rsi

print(dict_rsi)

# ohlcv = binance.fetch_ohlcv('BTC/USDT', '5m', limit=5)
# for item in ohlcv:
#     print(binance.iso8601(item[0]), item[1], item[2], item[3], item[4], item[5])

