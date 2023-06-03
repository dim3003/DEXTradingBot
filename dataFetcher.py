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


class DataFetcher():
    def __init__(self, binance_api_key, binance_api_secret, start_time, stop_time=datetime.utcnow(), symbol="BTCUSDT"):
        """
        Initialize the data fetcher
        """
        # Load binance client
        self.client = Client(binance_api_key, binance_api_secret)
        self.search_available_symbols = []
        self.start_time = int(start_time.timestamp()) * 1000
        self.stop_time = int(stop_time.timestamp()) * 1000
        self.symbol = symbol

    def list_available_symbols(self, search_term):
        """
        # Look for available symbols in binance and stores them in the class
        """
        data = self.client.get_all_tickers()
        self.search_available_symbols = [d['symbol']
                                         for d in data if search_term in d['symbol'].lower()]

    def fetch_price(self, symbol):
        """
        fetches the price of the selected cryptocurrency pair on binance
        """
        # Loop setup for data fetching (cap at 1000 rows)
        current_time = self.stop_time
        previous_time = int(
            (current_time - timedelta(hours=1000)).timestamp()) * 1000
        df_merge = pd.DataFrame()
        len_df = 1000
        i = 0

        while len_df > 990:
            print("Iteration number", i)

            # fetch 1 hour klines for Bitcoin data
            data = client.get_historical_klines(
                self.symbol, Client.KLINE_INTERVAL_1HOUR, str(previous_time), str(current_time))

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
            df_merge = pd.concat([df, df_merge])

            # Loop variables set
            len_df = len(df)
            i += 1
        df_merge.to_pickle(f"data/{self.symbol}.pkl")
        print(df_merge)
