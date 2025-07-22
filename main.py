import requests
from bs4 import BeautifulSoup
import time
import threading
from flask import Flask
import telegram

app = Flask(name)

TOKEN = "ТВОЙ_ТОКЕН"
CHAT_ID = "ТВОЙ_CHAT_ID"
bot = telegram.Bot(token=TOKEN)
seen_links = set()

def get_apartment_links():
    url = "https://www.saga.hamburg/immobiliensuche?Kategorie=APARTMENT"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    links = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "/immobiliensuche/immo-detail/" in href:
            full_url = f"https://www.saga.hamburg{href}"
            page = requests.get(full_url)
            inner = BeautifulSoup(page.text, "html.parser")
            apply_links = inner.find_all("a", href=True)
            for apply_a in apply_links:
                apply_href = apply_a["href"]
                if "tenant.immomio.com/apply" in apply_href:
                    if apply_href not in seen_links:
                        links.append(apply_href)
    return links

def run_bot():
    print("Бот запущен...")
    while True:
        try:
            new = [link for link in get_apartment_links() if link not in seen_links]
            for link in new:
                bot.send_message(chat_id=CHAT_ID, text=f"🏠 Новое жильё: {link}")
                seen_links.add(link)
        except Exception as e:
            print("Ошибка:", e)
        time.sleep(60)

# Flask — Render требует веб-сервер
@app.route('/')
def home():
    return "Apartment bot is running."

# Запуск бота в отдельном потоке
threading.Thread(target=run_bot).start()

if name == 'main':
    app.run(host="0.0.0.0", port=10000)
