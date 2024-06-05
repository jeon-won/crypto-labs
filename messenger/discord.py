# from dotenv import load_dotenv
# import os
import json
import requests

# load_dotenv()
# DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL")

def send_discord_message(webhook_url, message):
    """디스코드 웹훅을 사용하여 메시지를 보냅니다.

    Args:
      - webhook_url: 디스코드 채널 웹훅 URL
      - message: 보내려는 메시지(마크다운 일부 형식도 가능함)

    Returns: <class 'NoneType'>
    """
    headers = {
        'Content-Type': 'application/json',
    }

    data = {
        'content': message,
    }

    response = requests.post(webhook_url, headers=headers, data=json.dumps(data))

    if response.status_code == 204:
        print('Message successfully sent to Discord channel.')
    else:
        print(f'Failed to send message to Discord channel. Status code: {response.status_code}')

# send_discord_message(DISCORD_WEBHOOK_URL, "Message")