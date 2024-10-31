import requests

def get_exchange_rate(from_currency, to_currency):
    api_key = '8e4519666ae74e6ab7f5fa3b15f2f95e'
    url = f"https://api.currencyfreaks.com/v2.0/rates/latest?apikey={api_key}&symbols={from_currency},{to_currency}"

    try:
        response = requests.get(url)
        data = response.json()
        rate = data['rates'][from_currency]
        print(data)
        print(rate)
        return float(rate)
    except Exception as e:
        print(f"Error fetching exchange rate: {e}")
        return None


def convert_currency(request):
    from_currency = "VND"
    to_currency = "USD"

    rate = get_exchange_rate(from_currency, to_currency)
    print(rate)
    if rate:
        amount_vnd = request.get('amount', 1000000)
        amount_usd = amount_vnd / rate
        print('1,000,000 VND = {:.2f} USD'.format(amount_usd))
        return '1,000,000 VND = {:.2f} USD'.format(amount_usd)
    else:
        return 'Error fetching exchange rate'


request = {'GET': {'amount': 1000000}}
convert_currency(request)
