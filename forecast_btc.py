import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
import ccxt

# 데이터 가져오기
binance = ccxt.binance(config={
    'options': {
        'defaultType': 'future'
    }
})
ohlcv = binance.fetch_ohlcv("BTC/USDT", "1d", limit=365)

# ohlcv 데이터를 DataFrame으로 변환
df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

# Feature 생성: 종가 & 변화율(PER)
df['per_change'] = df['close'].pct_change().fillna(0)  # 종가의 퍼센트 변화율
data = df[['close', 'per_change']].values

# 데이터 스케일링
from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler()
data_scaled = scaler.fit_transform(data)

# 학습 데이터 준비
def create_sequences(data, seq_length=60):
    sequences = []
    labels = []
    for i in range(seq_length, len(data)):
        sequences.append(data[i-seq_length:i])
        labels.append(data[i, 0])  # 종가 예측
    return np.array(sequences), np.array(labels)

seq_length = 60
X, y = create_sequences(data_scaled, seq_length)

# Train-Test Split
train_size = int(len(X) * 0.8)
X_train, X_test = X[:train_size], X[train_size:]
y_train, y_test = y[:train_size], y[train_size:]

# LSTM 모델 생성
model = Sequential([
    LSTM(64, return_sequences=True, input_shape=(X_train.shape[1], X_train.shape[2])),
    Dropout(0.2),
    LSTM(32, return_sequences=False),
    Dense(16, activation='relu'),
    Dense(1)  # 종가 예측
])

model.compile(optimizer='adam', loss='mean_squared_error')

# 모델 학습
history = model.fit(X_train, y_train, epochs=20, batch_size=32, validation_data=(X_test, y_test))

# 향후 10개의 캔들 예측
def predict_future(data, model, scaler, steps=10):
    future_predictions = []
    last_sequence = data[-seq_length:]

    for _ in range(steps):
        prediction = model.predict(last_sequence[np.newaxis, :, :])[0, 0]
        future_predictions.append(prediction)
        new_entry = np.array([[prediction, 0]])  # 변화율은 0으로 대체
        last_sequence = np.vstack([last_sequence[1:], new_entry])

    future_predictions = scaler.inverse_transform(np.array(future_predictions).reshape(-1, 2))[:, 0]
    return future_predictions

# 예측 수행
future_predictions = predict_future(data_scaled, model, scaler)

# 시각화
plt.figure(figsize=(12, 6))
plt.plot(df['timestamp'], df['close'], label='Actual Close Price', color='blue')
future_timestamps = pd.date_range(df['timestamp'].iloc[-1], periods=len(future_predictions) + 1, freq='15T')[1:]
plt.plot(future_timestamps[:len(future_predictions)], future_predictions, label='Predicted Close Price', color='red')
plt.title('BTC/USDT Close Price Prediction (Next 10 Candles)')
plt.xlabel('Time')
plt.ylabel('Close Price (USD)')
plt.legend()
plt.show()


"""
아래 코드는 파이썬의 ccxt를 사용하여 비트코인 ohlcv(시가, 고가, 저가, 종가) 데이터를 가져오는 코드입니다.

python
import ccxt

binance = ccxt.binance(config={
    'options': {
        'defaultType': 'future'
    }
})
ohlcv = binance.fetch_ohlcv("BTC/USDT", "15m", limit=300)


이 ohlcv 값을 사용하여 향후 10개의 캔들이 어떻게 생성될지 예측하는 파이썬 코드를 만들어 주세요. 조건은 아래와 같습니다.
1. 종가와 PER을 사용하여 파이썬 텐서플로를 통한 LSTM 모델을 이용
2. 예측한 것을 시각화
"""