import sqlite3
import requests
from bs4 import BeautifulSoup
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.dispatcher.filters import Command
from aiogram import executor
from config import token

bot = Bot(token=token)
dp = Dispatcher(bot)

def init_db():
    conn = sqlite3.connect('news.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            url TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def add_news_to_db(title, url):
    conn = sqlite3.connect('news.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO news (title, url) VALUES (?, ?)', (title, url))
    conn.commit()
    conn.close()

async def start(message: Message):
    await message.answer("Привет! Я бот новостей. Чтобы получить новости, введите команду /news.")

async def news(message: Message):
    for page in range(1, 11):
        url = f'https://24.kg/page_{page}'
        try:
            response = requests.get(url=url)
            response.raise_for_status()  
            soup = BeautifulSoup(response.text, 'html.parser')
            all_news = soup.find_all('div', class_='one')
            for news_item in all_news:
                news_title_div = news_item.find('div', class_='title')
                news_link = news_item.find('a')
                if news_title_div and news_link:
                    news_title = news_title_div.text.strip()
                    news_url = f"https://24.kg{news_link['href']}" 
                    add_news_to_db(news_title, news_url)
                    news_text = f"*{news_title}*"  
                    while len(news_text) > 0:
                        await message.answer(news_text[:4096], parse_mode="Markdown")
                        news_text = news_text[4096:]
        except Exception as e:
            await message.answer(f"Произошла ошибка при получении новостей: {e}")

dp.message_handler(Command('start'))(start)
dp.message_handler(Command('news'))(news)

if __name__ == '__main__':
    init_db()  
    executor.start_polling(dp, skip_updates=True)
