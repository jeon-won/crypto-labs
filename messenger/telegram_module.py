# from dotenv import load_dotenv
# import asyncio
# import os
import telegram

# load_dotenv()
# TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
# TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

async def send_telegram_message(token, chat_id, message):
    """텔레그램 메시지를 보냅니다.
    
    Args:
      - token: 텔레그램 봇 토큰 값
      - chat_id: 메시지를 수신할 챗 아이디(조회 방법: 봇과 적어도 한 번 대화한 다음 https://api.telegram.org/bot봇토큰값/getUpdates 접속 후 "message": { "id" } 속성 값 확인)

    Returns: <class 'NoneType'>
    """
    bot = telegram.Bot(token)
    await bot.send_message(chat_id=chat_id, text=message)
    
# asyncio.run(send_telegram_message(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, "Message"))