import os
import pandas as pd
from dotenv import load_dotenv
from binance import Client
from datetime import datetime, timedelta
#pd.set_option('display.max_rows', None)


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

# Setup timestamps for the loop (beginning now)
now = datetime.utcnow()
current_time = int(now.timestamp()) * 1000
previous_time = int((now - timedelta(hours=1000)).timestamp()) * 1000

# Make the dataframe
dfAll = pd.DataFrame()

# Setup loop variables
lenDF = 1000
i = 0

while lenDF > 990:

    print("Iteration number", i)
    # fetch 1 hour klines for Bitcoin data
    data = client.get_historical_klines(
        "BTCUSDT", Client.KLINE_INTERVAL_1HOUR, str(previous_time), str(current_time))

    # Create a dataframe from the data
    df = pd.DataFrame(data, columns=["Open time", "Open", "High", "Low", "Close", "Volume", "Close time",
                                     "Quote asset volume", "Number of trades", "Taker buy base asset volume", "Taker buy quote asset volume", "Ignore"])

    # Set the "Close time" column as the index
    df.set_index("Close time", inplace=True)

    # Remove all other columns except Close price
    df = df.drop(
        df.columns.difference(['Close']), axis=1)

    # Rename the index and column
    df = df.rename(columns={'Close': 'close_price'})
    df = df.rename_axis('time')

    # Change the timestamps for next loop
    current_time = current_time - 3.6e9  # minus 1000 hours in milliseconds
    previous_time = previous_time - 3.6e9

    # Merge into the dataframe
    dfAll = pd.concat([df, dfAll])

    # Loop variables set
    lenDF = len(df)
    i += 1

dfAll.to_pickle("bitcoin_price.pkl")
print(dfAll)
