from datetime import datetime
import ccxt, time
import pyaudio, wave  # MacOS인 경우 사전에 `brew install portaudio` 명령어 실행해야 됨
"""
# scan_vol_burst.py
* 기능: 초당 발생한 거래량이 일정 이상일 때 사운드를 재생합니다.
* 사용법: scan_vol_burst.py 파일을 열어 상수 값 입력 후 실행
"""



# 사운드 재생 함수
def play_sound(wav_path):
    # wave 파일 열기
    wf = wave.open(wav_path, 'rb')
    pa = pyaudio.PyAudio()

    # 오디오 스트림 열기
    stream = pa.open(
        format=pa.get_format_from_width(wf.getsampwidth()),
        channels=wf.getnchannels(),
        rate=wf.getframerate(),
        output=True
    )

    # 일정 크기씩 프레임을 읽어 스트림에 출력
    chunk = 1024
    data = wf.readframes(chunk)
    while data:
        stream.write(data)
        data = wf.readframes(chunk)

    # 스트림 종료 및 종료
    stream.stop_stream()
    stream.close()
    pa.terminate()


# 상수 및 변수
SYMBOL = 'BTC/USDT'
THRESHOLD = 100  # 초당 거래량이 이 이상이면 사운드 출력
exchange = ccxt.binance({
    'enableRateLimit': True,
    'options': {
        'defaultType': 'future'
    }
})

# 초기 거래량 조회
ticker = exchange.fetch_ticker(SYMBOL)
prev_volume = ticker['baseVolume']
print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}, 초기 거래량: {prev_volume:.1f}")

# 매 1초마다 거래량 확인
while True:
    try:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ticker = exchange.fetch_ticker(SYMBOL)
        current_volume = ticker['baseVolume']
        volume_diff = current_volume - prev_volume
        print(f"{current_time} | 이전 거래량: {prev_volume:.1f} | 현재 거래량: {current_volume:.1f} | 차이: {volume_diff:.1f}")

        ## 거래량 차이가 THRESHOLD 이상이면 사운드 출력
        if volume_diff >= THRESHOLD:
            print("⭐️⭐️⭐️⭐️⭐️ 거래량 터짐 ⭐️⭐️⭐️⭐️⭐️")
            play_sound('./lib/alert.wav')

        ## 현재 거래량을 다음 비교를 위해 저장
        prev_volume = current_volume

    except Exception as e:
        print(f"오류 발생: {e}")

    time.sleep(1)