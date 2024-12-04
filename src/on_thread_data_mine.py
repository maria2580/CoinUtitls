from os import error
import requests
import time
import csv
import threading
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QHBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import os


def get_exchange_rate():
    url = 'https://api.exchangerate-api.com/v4/latest/USD'
    response = requests.get(url)
    data = response.json()
    return data['rates']['KRW']


def get_upbit_price(market):
    url = f"https://api.upbit.com/v1/ticker?markets={market}"
    response = requests.get(url)
    data = response.json()
    return data[0]['trade_price']


def get_binance_price(symbol):
    if symbol == 'USDT':
        return 1.0
    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}USDT"
    response = requests.get(url)
    if response.status_code != 200:
        raise ValueError(f"Failed to get price for {symbol}: {response.json().get('msg')}")

    # 확인: 사용한 요청 횟수를 출력
    used_weight = response.headers.get('X-MBX-USED-WEIGHT-1M', 'N/A')
    print(f"현재 사용한 요청 횟수 (1분 기준): {used_weight}")

    data = response.json()
    return float(data['price'])


def get_binance_network_fee(symbol):
    # Hardcoded network fees as a temporary solution to avoid authorization issues
    network_fees = {
        'XRP': 1,  # Example fee in XRP
        'TRX': 10,  # Example fee in TRX
        'USDT': 1  # Example fee in USDT
    }
    return network_fees.get(symbol, None)


def calculate_transfer_value(krw_balance):
    markets = {
        'XRP': {'upbit': 'KRW-XRP', 'binance': 'XRP'},
        'TRX': {'upbit': 'KRW-TRX', 'binance': 'TRX'},
        'USDT': {'upbit': 'KRW-USDT', 'binance': 'USDT'}
    }

    results = {}

    for coin, market in markets.items():
        upbit_price_krw = get_upbit_price(market['upbit'])
        binance_price_usd = get_binance_price(market['binance'])
        network_fee = get_binance_network_fee(market['binance'])
        if network_fee is None:
            continue

        amount_purchased = krw_balance / upbit_price_krw
        amount_transferred = amount_purchased - network_fee

        if coin == 'USDT':
            value_after_transfer = amount_transferred
        else:
            value_after_transfer = amount_transferred * binance_price_usd

        results[coin] = value_after_transfer
        print(
            f"업비트에서 바이낸스로 출금시: {krw_balance} KRW -> {coin} : {amount_purchased:.4f}개 -> 네트워크 피 계산 뒤 바이낸스 : {coin} {amount_transferred:.4f}개 -> 바이낸스의 {coin} 가격으로 계산된 USDT의 양: {value_after_transfer:.5f} USDT")

    print("\n최종 결과:")
    print(f"KRW -> XRP -> USDT: {results.get('XRP', 0):.5f} USDT")
    print(f"KRW -> TRX -> USDT: {results.get('TRX', 0):.5f} USDT")
    print(f"KRW -> USDT 송금 후: {results.get('USDT', 0):.5f} USDT")

    return results


class LivePlot(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KRW to USDT Value After Transfer")
        self.setGeometry(100, 100, 1280, 720)

        self.main_widget = QWidget(self)
        self.setCentralWidget(self.main_widget)
        layout = QVBoxLayout(self.main_widget)

        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        self.ax.set_xlabel("Time")
        self.ax.set_ylabel("USDT Value")
        self.ax2 = self.ax.twinx()
        self.ax2.set_ylabel("Exchange Rate")
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
        self.ax.xaxis.set_major_locator(mdates.MinuteLocator(interval=1))
        self.ax.grid(True)

        self.timestamp_data = []
        self.xrp_data = []
        self.trx_data = []
        self.usdt_data = []
        self.exchange_rate_data = []

        # Load existing data if the file exists
        if os.path.exists('transfer_data.csv'):
            self.load_existing_data()

        # Create buttons for different timeframes
        button_layout = QHBoxLayout()
        self.timeframes = ['1s', '10s', '30s', '1min', '3min', '5min', '15min', '30min', '1h', '4h', '1d']
        for timeframe in self.timeframes:
            button = QPushButton(timeframe)
            button.clicked.connect(lambda checked, tf=timeframe: self.plot_average(tf))
            button_layout.addWidget(button)

        layout.addLayout(button_layout)

        self.current_timeframe = '1s'  # Set the default chart state to '1s'

    def load_existing_data(self):
        try:
            existing_data = pd.read_csv('transfer_data.csv')
            for _, row in existing_data.iterrows():
                timestamp = pd.to_datetime(row['timestamp'])
                self.timestamp_data.append(timestamp)
                self.xrp_data.append(row['xrp_value'])
                self.trx_data.append(row['trx_value'])
                self.usdt_data.append(row['usdt_value'])
                self.exchange_rate_data.append(row['exchange_rate'])

            # Plot the existing data
            self.update_plot(None, None, None, None, None)
        except Exception as e:
            print(f"Error loading existing data: {e}")

    def update_plot(self, timestamp, xrp_value, trx_value, usdt_value, exchange_rate):

        if timestamp is not None:
            self.timestamp_data.append(timestamp)
            self.xrp_data.append(xrp_value)
            self.trx_data.append(trx_value)
            self.usdt_data.append(usdt_value)
            self.exchange_rate_data.append(exchange_rate)

        self.plot_average(self.current_timeframe)

    def plot_average(self, timeframe):
        self.current_timeframe = timeframe  # Save the selected chart state

        try:
            df = pd.DataFrame({
                'timestamp': self.timestamp_data,
                'xrp_value': self.xrp_data,
                'trx_value': self.trx_data,
                'usdt_value': self.usdt_data,
                'exchange_rate': self.exchange_rate_data
            })
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df.set_index('timestamp', inplace=True)

            # Resample the data based on the selected timeframe
            if timeframe == '1s':
                resampled_df = df.resample('1s').mean()
            elif timeframe == '10s':
                resampled_df = df.resample('10s').mean()
            elif timeframe == '30s':
                resampled_df = df.resample('30s').mean()
            elif timeframe == '1min':
                resampled_df = df.resample('1min').mean()
            elif timeframe == '3min':
                resampled_df = df.resample('3min').mean()
            elif timeframe == '5min':
                resampled_df = df.resample('5min').mean()
            elif timeframe == '15min':
                resampled_df = df.resample('15min').mean()
            elif timeframe == '30min':
                resampled_df = df.resample('30min').mean()
            elif timeframe == '1h':
                resampled_df = df.resample('1h').mean()
            elif timeframe == '4h':
                resampled_df = df.resample('4h').mean()
            elif timeframe == '1d':
                resampled_df = df.resample('1D').mean()
            else:
                return

            resampled_df.dropna(inplace=True)

            # Plot the resampled data
            self.ax.clear()
            self.ax2.clear()

            self.ax.plot(resampled_df.index, resampled_df['xrp_value'], label="XRP to USDT", color="blue")
            self.ax.plot(resampled_df.index, resampled_df['trx_value'], label="TRX to USDT", color="orange")
            self.ax.plot(resampled_df.index, resampled_df['usdt_value'], label="USDT to USDT", color="green")
            self.ax2.plot(resampled_df.index, resampled_df['exchange_rate'], label="Exchange Rate (krw/usd)", color="grey", linestyle="--")

            self.ax.set_xlabel("Time")
            self.ax.set_ylabel("USDT Value")
            self.ax.legend(loc="upper left")
            self.ax2.set_ylabel("Exchange Rate")
            self.ax2.legend(loc="upper right")

            self.ax.grid(True)
            self.canvas.draw()

        except Exception as e:
            print(f"Error plotting data: {e}")


def save_data_to_file(data):
    try:
        if os.path.exists('transfer_data.csv'):
            existing_data = pd.read_csv('transfer_data.csv')
            df = pd.concat([existing_data, pd.DataFrame(data)], ignore_index=True)
        else:
            df = pd.DataFrame(data)
        df.to_csv('transfer_data.csv', index=False)
        print("데이터가 transfer_data.csv 파일에 저장되었습니다.")
    except Exception as e:
        print(f"Error saving data: {e}")


def run_periodic_task(live_plot):
    krw_balance = 10000000
    exchange_rate = get_exchange_rate()

    while True:
        results = calculate_transfer_value(krw_balance)
        results['timestamp'] = pd.Timestamp.now()
        results['exchange_rate'] = exchange_rate

        save_data_to_file([results])

        live_plot.update_plot(results['timestamp'], results.get('XRP', None), results.get('TRX', None), results.get('USDT', None), results['exchange_rate'])

        time.sleep(1)


def main():
    app = QApplication([])
    live_plot = LivePlot()
    live_plot.show()

    data_thread = threading.Thread(target=run_periodic_task, args=(live_plot,))
    data_thread.daemon = True
    data_thread.start()

    app.exec_()


if __name__ == "__main__":
    main()
