import requests
import os
from src.exchange_rate import get_exchange_rate


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


def calculate_transfer_value(krw_balance, exchange_rate):
    """
    Calculate the value of each coin after purchasing from Upbit and transferring to Binance.

    Args:
    krw_balance (float): Amount of KRW available to invest.
    exchange_rate (float): Current exchange rate from KRW to USD.

    Returns:
    None
    """
    markets = {
        'XRP': {'upbit': 'KRW-XRP', 'binance': 'XRP'},
        'TRX': {'upbit': 'KRW-TRX', 'binance': 'TRX'},
        'USDT': {'upbit': 'KRW-USDT', 'binance': 'USDT'}
    }

    results = {}

    for coin, market in markets.items():
        # Get prices from Upbit and Binance
        upbit_price_krw = get_upbit_price(market['upbit'])
        binance_price_usd = get_binance_price(market['binance'])

        # Get network fee for the coin from Binance
        network_fee = get_binance_network_fee(market['binance'])
        if network_fee is None:
            continue

        # Calculate the amount of coin that can be purchased on Upbit
        amount_purchased = krw_balance / upbit_price_krw

        # Subtract network fee to get the amount transferred to Binance
        amount_transferred = amount_purchased - network_fee

        # Calculate the value in Binance after transfer in terms of USDT
        if coin == 'USDT':
            value_after_transfer = amount_transferred  # USDT remains as is after transfer
        else:
            value_after_transfer = amount_transferred * binance_price_usd

        # Store the result for summary
        results[coin] = value_after_transfer

        # Print the detailed results
        print(
            f"업비트에서 바이낸스로 출금시: {krw_balance} KRW -> {coin} : {amount_purchased:.4f}개 -> 네트워크 피 계산 뒤 바이낸스 : {coin} {amount_transferred:.4f}개 -> 바이낸스의 {coin} 가격으로 계산된 USDT의 양: {value_after_transfer:.5f} USDT")

    # Print the summary results
    print("\n최종 결과:")
    print(f"KRW -> XRP -> USDT: {results.get('XRP', 0):.5f} USDT")
    print(f"KRW -> TRX -> USDT: {results.get('TRX', 0):.5f} USDT")
    print(f"KRW -> USDT 송금 후: {results.get('USDT', 0):.5f} USDT")


def main():
    krw_balance = 10000000  # 1,000,000 KRW
    exchange_rate = get_exchange_rate()

    calculate_transfer_value(krw_balance, exchange_rate)


if __name__ == "__main__":
    main()
