import requests
from django.conf import settings

BOT_TOKEN = settings.TELEGRAM_BOT_TOKEN
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def send_message(chat_id, text):
    url = f"{BASE_URL}/sendMessage?chat_id={chat_id}&text={text}"
    try:
        requests.get(url)
    except requests.exceptions.RequestException as e:
        print(f"Send message Error: {e}")