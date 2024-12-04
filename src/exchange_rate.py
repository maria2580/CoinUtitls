import requests

def get_exchange_rate():
    url = 'https://api.exchangerate-api.com/v4/latest/USD'
    response = requests.get(url)
    data = response.json()
    return data['rates']['KRW']

# 사용 예시

if __name__ == "__main__":
    exchange_rate = get_exchange_rate()
    print(f"현재 USD/KRW 환율은: {exchange_rate}입니다.")
