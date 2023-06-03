import os
import pandas as pd
from dotenv import load_dotenv
from binance import Client
from datetime import datetime, timedelta
# pd.set_option('display.max_rows', None)

# Load environment variables from the .env file
load_dotenv()

# Retrieve the values of api_key_binance and api_secret_binance
API_KEY = os.getenv('API_KEY_BINANCE')
API_SECRET = os.getenv('API_SECRET_BINANCE')


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
        merged_df = pd.DataFrame()
        row_len = 1000
        iteration_count = 0

        while row_len > 990:
            print("Iteration count: ", iteration_count)

            # fetch 1 hour klines for Bitcoin data
            data = client.get_historical_klines(
                self.symbol, Client.KLINE_INTERVAL_1HOUR, str(previous_time), str(current_time))

            # Create a dataframe from the data
            df = self._create_dataframe_from_data(data)

            # Change the timestamps for next loop
            current_time -= self._get_milliseconds(1000)
            previous_time -= self._get_milliseconds(1000)

            # Merge into the dataframe
            merged_df = pd.concat([df, merged_df])

            # Loop variables set
            row_len = len(df)
            iteration_count += 1
        merged_df.to_pickle(f"data/{self.symbol}.pkl")
        print(merged_df)

    @staticmethod
    def _create_dataframe_from_data(data):
        df = pd.DataFrame(data, columns=["Open time", "Open", "High", "Low", "Close", "Volume", "Close time",
                                         "Quote asset volume", "Number of trades", "Taker buy base asset volume", "Taker buy quote asset volume", "Ignore"])

        df.set_index("Close time", inplace=True)

        df = df[['Close']].rename(
            columns={'Close': 'close_price'}).rename_axis('time')

        return df

    @staticmethod
    def _get_milliseconds(hours):
        return hours * 60 * 60 * 1000
