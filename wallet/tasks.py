import requests
from django.conf import settings as setting
from django.core.cache import cache


def get_exchange_rate(from_currency, to_currency):
    cache_key = f"exchange_rate_{from_currency}_{to_currency}"
    cached_rate = cache.get(cache_key)
    if cached_rate:
        return cached_rate

    api_key = setting.CURRENCYFREAKS_API_KEY
    url = f"https://api.currencyfreaks.com/latest?apikey={api_key}&symbols={from_currency},{to_currency}"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()

        from_rate = float(data['rates'][from_currency])
        to_rate = float(data['rates'][to_currency])

        # Calculate the exchange rate
        rate = to_rate / from_rate

        # Cache the result for 1 hour (3600 seconds)
        cache.set(cache_key, rate, 3600)

        return rate
    except requests.RequestException as e:
        return None
    except (KeyError, ValueError) as e:
        return None


def convert_currency(amount, from_currency="VND", to_currency="USD"):
    rate = get_exchange_rate(from_currency, to_currency)
    if rate is None:
        return None

    try:
        amount = float(amount)
        converted_amount = amount * rate
        return round(converted_amount, 2)
    except ValueError:
        return None


def format_currency_conversion(amount, from_currency="VND", to_currency="USD"):
    converted_amount = convert_currency(amount, from_currency, to_currency)
    if converted_amount is None:
        return 'Error converting currency'

    return f'{amount:,.0f} {from_currency} = {converted_amount:,.2f} {to_currency}'
