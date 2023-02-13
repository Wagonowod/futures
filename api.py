import requests
from datetime import datetime, timedelta

from timeloop import Timeloop
import time
from decimal import Decimal

tickers = ['XRPUSDT']
tl = Timeloop()


class PriceObserver:

    def __init__(self, ticker):
        self.ticker = ticker
        self.url = f'https://fapi.binance.com/fapi/v1/markPriceKlines?symbol={ticker}&interval=1m&limit=60'
        self.percentage_price_change = 1
        self.message_time = None
        self.message_sending_time = timedelta(hours=1)

    def check(self):
        klines = self.get_klines()
        max_price = self.get_max_price(klines)
        current_price = self.get_current_price(klines)
        difference = self.get_difference(max_price, current_price)
        self.send_message(difference, current_price, max_price)

    def get_klines(self):
        return requests.get(self.url).json()

    def get_max_price(self, klines):
        max_price = []
        for item in klines:
            max_price.append(item[2])
        return Decimal(max(max_price))

    def get_current_price(self, klines):
        return Decimal(klines[-1][4])

    def get_difference(self, max_price, current_price):
        return Decimal(100 - (current_price / max_price) * 100)

    def send_message(self, difference, current_price, max_price):
        if difference >= self.percentage_price_change:
            if self.message_time is None or self.message_time >= self.message_time + self.message_sending_time:
                print(
                    f"Цена за последний час изменилась больше чем на 1%, текущая цена {self.ticker}: {current_price}, максимальная цена {self.ticker}: {max_price}. ")
                self.message_time = datetime.now()


observers = []
for ticker in tickers:
    observers.append(PriceObserver(ticker))


@tl.job(interval=timedelta(seconds=1 // 1000000))
def main():
    for observer in observers:
        observer.check()


tl.start()
while True:
    try:
        time.sleep(1)
    except KeyboardInterrupt:
        tl.stop()
        break
