# ---------------------------------------------------------------
# # okx/webhook.py
#  * Flask 서버를 사용하여 트레이딩뷰 웹훅 메시지를 받아 처리하는 코드(작성 중)
# ---------------------------------------------------------------

from dotenv import load_dotenv
from flask import Flask, request, jsonify
from logging.handlers import RotatingFileHandler
import logging
import os

# ----- 상수 및 변수 -----

load_dotenv()
PORT = os.environ.get("FLASK_PORT")
ALLOWED_IPS = ["52.89.214.238", "34.212.75.30", "54.218.53.128", "52.32.178.7"]  ## 트레이딩뷰 IP

per_sl = 1
per_tp = 2

# ----- Flask 서버 초기 설정 -----

app = Flask(__name__)

# # 특정 IP만 접속 허용
# @app.before_request
# def limit_remote_addr():
#     client_ip = request.remote_addr
#     if client_ip not in ALLOWED_IPS:
#         return jsonify({"status": "failure", "message": "Access denied."}), 403

# ----- 로그 설정 -----

# 파일 로그 핸들러 설정
file_handler = RotatingFileHandler('app.log', maxBytes=10000, backupCount=1)
file_handler.setLevel(logging.INFO)

# # 콘솔 로그 핸들러 설정(선택사항)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# 로그 포맷 설정
formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Flask 애플리케이션에 핸들러 추가
app.logger.setLevel(logging.INFO)
app.logger.addHandler(file_handler)
app.logger.addHandler(console_handler)

# ----- 라우팅 -----

# @app.route('/', methods=['GET'])
# def index():
#     if request.method == 'GET':
#         app.logger.info('Hello, this is an info message')
#         return "<h1>Hello!</h1>", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        data = request.json # 전송받은 데이터
        ticker = data["ticker"]
        interval = data["interval"]
        divergence = data["divergence"]
        close = float(data["close"])
        price_sl = 0.0
        price_tp = 0.0
        msg = ""

        if(divergence == 'bull'):    # 롱 포지션
            price_sl = round(close * (100-per_sl)/100, 1)
            price_tp = round(close * (100+per_tp)/100, 1)
            msg = f"{ticker} {interval} {divergence} {close} -> Long StopLoss: {price_sl}, TakeProfit: {price_tp}"
        elif(divergence == 'bear'):  # 숏 포지션
            price_sl = round(close * (100+per_sl)/100, 1)
            price_tp = round(close * (100-per_tp)/100, 1)
            msg = f"{ticker} {interval} {divergence} {close} -> Short StopLoss: {price_sl}, TakeProfit: {price_tp}"

        app.logger.info(msg)
        
        return jsonify({"status": "success"}), 200
    else:
        return jsonify({"status": "failure", "message": "Invalid request method"}), 400

if __name__ == '__main__':
    app.run(debug=False, host="0.0.0.0", port=PORT)