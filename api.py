import requests
from datetime import datetime, timedelta
from timeloop import Timeloop
import time
from decimal import Decimal

tl = Timeloop()
percentage_price_change = 1
message_time = None
message_sending_time = timedelta(hours=1)


@tl.job(interval=timedelta(seconds=1 // 1000000))
def main():
    url = 'https://fapi.binance.com/fapi/v1/markPriceKlines?symbol=XRPUSDT&interval=30m&limit=2'
    klines = get_klines(url)
    max_price = get_max_price(klines)
    current_price = get_current_price(klines)
    difference = get_difference(max_price, current_price)
    send_message(difference, current_price, max_price)


def get_klines(url):
    return requests.get(url).json()


def get_max_price(klines):
    max_price = []
    for item in klines:
        max_price.append(item[2])
    return Decimal(max(max_price))


def get_current_price(klines):
    for item in klines:
        if item == klines[-1]:
            return Decimal(item[4])


def get_difference(max_price, current_price):
    return Decimal(100 - (current_price / max_price) * 100)


def send_message(difference, current_price, max_price):
    global message_time
    if difference >= percentage_price_change:
        if message_time is None or message_time >= message_time + message_sending_time:
            print(
                f"Цена за последний час изменилась больше чем на 1%, текущая цена: {current_price}, максимальная цена: {max_price}. ")
            message_time = datetime.now()


tl.start()
while True:
    try:
        time.sleep(1)
    except KeyboardInterrupt:
        tl.stop()
        break
