import asyncio
import aiohttp
import ast
import requests
from dotenv import load_dotenv
import telebot
import os

load_dotenv()

bot = telebot.TeleBot(os.getenv('TELEGRAM_BOT_TOKEN'))
url_send = (f'https://api.telegram.org/bot'
            f'{os.getenv("TELEGRAM_BOT_TOKEN")}/sendMessage')
chat_id = '849055520'


async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()


async def get_futures_data(session, symbol, interval='1m'):
    url = (f"https://fapi.binance.com/fapi/v1/klines?symbol={symbol}&"
           f"interval={interval}&limit=10")
    response = await fetch(session, url)
    return response


def get_futures():
    symbols = []  # список фьючерсов
    # Получение списка монет, доступных для торговли фьючерсами
    exchange_info_url = "https://fapi.binance.com/fapi/v1/exchangeInfo"
    exchange_info_response = requests.get(exchange_info_url)
    exchange_info_data = exchange_info_response.json()

    for symbol_info in exchange_info_data['symbols']:
        symbol = symbol_info['symbol']
        if symbol.endswith("USDT"):
            symbols.append(symbol)
    return symbols


async def main():
    symbols = get_futures()
    interval = '5m'
    tasks = []

    async with aiohttp.ClientSession() as session:
        for symbol in symbols:
            task = asyncio.ensure_future(get_futures_data(session, symbol,
                                                          interval))
            tasks.append(task)

        responses = await asyncio.gather(*tasks)
        for i, response in enumerate(responses[:-1]):

            tree = ast.parse(response, mode='eval')
            # Извлечение значения из AST и преобразование его в список
            result = ast.literal_eval(tree.body)

            start_price = float(result[0][1])  # цена открытия первой свечи
            end_price = float(result[-1][4])  # цена закрытия последней свечи
            # Вычисление процента
            price_change_percent = 1 - (end_price/start_price)

            if abs(price_change_percent) >= float(0.05):
                print(symbols[i])
                message = (f"https://www.binance.com/en/futures/{symbols[i]}\n"
                           f"Symbol: {symbols[i]}, Price Change Percent: "
                           f"{price_change_percent*100:.2f}%")
                send_message(message)


def send_message(message):
    params = {
        'chat_id': chat_id,
        'text': message
    }
    requests.get(url_send, params=params)


asyncio.run(main())
