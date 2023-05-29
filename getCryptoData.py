import os
from dotenv import load_dotenv
from binance import Client

# Load environment variables from the .env file
load_dotenv()

# Retrieve the values of api_key_binance and api_secret_binance
api_key = os.getenv('api_key_binance')
api_secret = os.getenv('api_secret_binance')

# Load binance client
client = Client(api_key, api_secret)

"""
# Look for symbol BTC
data = client.get_all_tickers()
btc_symbols = [d['symbol'] for d in data if 'btc' in d['symbol'].lower()]
print(btc_symbols)
"""

# fetch 1 hour klines for Bitcoin data
klines = client.get_historical_klines(
    "BTCUSDT", Client.KLINE_INTERVAL_1HOUR, "1 Dec, 2017", "2 Dec, 2017")

print(klines)
