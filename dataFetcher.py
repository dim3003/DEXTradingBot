import os
import pandas as pd
from dotenv import load_dotenv
from binance import Client
from datetime import datetime, timedelta


class DataFetcher():
    """
    A class used to fetch data from Binance.

    Attributes
    ----------
    client : binance.Client
        The Binance client used to fetch data.
    search_available_symbols : list
        A list to store the available symbols from Binance.
    start_time : int
        The start timestamp (in ms) for fetching data.
    stop_time : int
        The stop timestamp (in ms) for fetching data.
    symbol : str
        The symbol for which to fetch data.
    """

    def __init__(self, binance_api_key, binance_api_secret, stop_time=datetime.utcnow(), symbol="BTCUSDT"):
        """
        Constructs all the necessary attributes for the data fetcher object.

        Parameters
        ----------
        binance_api_key : str
            The Binance API key.
        binance_api_secret : str
            The Binance API secret.
        stop_time : datetime.datetime, optional
            The stop datetime for fetching data (default is current UTC time).
        symbol : str, optional
            The symbol for which to fetch data (default is "BTCUSDT").
        """
        self.client = Client(binance_api_key, binance_api_secret)
        self.search_available_symbols = []
        self.stop_time = int(stop_time.timestamp()) * 1000
        self.symbol = symbol

    def list_available_symbols(self, search_term):
        """
        Fetches and stores the available symbols from Binance that contain the given search term.

        Parameters
        ----------
        search_term : str
            The search term to use when looking for symbols.
        """
        search_term = search_term.lower()
        data = self.client.get_all_tickers()
        self.search_available_symbols = [
            d['symbol'] for d in data if search_term in d['symbol'].lower()]
        print(self.search_available_symbols)

    def fetch_price(self):
        """
        Fetches the price data for the given symbol.

        The method fetches 1 hour klines (OHLCV) data, creates a DataFrame with this data, processes it and stores it as a pickle file. 
        The process is repeated in a loop until the number of rows in the fetched data falls below 990.

        """
        current_time = self.stop_time
        previous_time = current_time - self._get_milliseconds(1000)

        merged_df = pd.DataFrame()
        row_len = 1000  # initial row length
        iteration_count = 0

        while row_len > 990:
            print(f"Iteration count: {iteration_count}")

            data = self.client.get_historical_klines(
                self.symbol, Client.KLINE_INTERVAL_1HOUR, str(previous_time), str(current_time))

            df = self._create_dataframe_from_data(data)

            # Adjust the timestamps for the next loop iteration
            current_time -= self._get_milliseconds(1000)
            previous_time -= self._get_milliseconds(1000)

            # Merge the new DataFrame with the main one
            merged_df = pd.concat([df, merged_df])

            # Update loop variables
            row_len = len(df)
            iteration_count += 1

        # Store the final DataFrame as a pickle file
        merged_df.to_pickle(f"data/{self.symbol}.pkl")

        print(merged_df)

    @staticmethod
    def _create_dataframe_from_data(data):
        """
        Creates a DataFrame from the given data, keeps only the 'Close' price column and renames it to 'close_price'.

        Parameters
        ----------
        data : list
            The data from which to create a DataFrame.

        Returns
        -------
        pandas.DataFrame
            The created DataFrame.
        """
        df = pd.DataFrame(data, columns=["Open time", "Open", "High", "Low", "Close", "Volume", "Close time",
                                         "Quote asset volume", "Number of trades", "Taker buy base asset volume", "Taker buy quote asset volume", "Ignore"])

        df.set_index("Close time", inplace=True)
        df = df[['Close']].rename(
            columns={'Close': 'close_price'}).rename_axis('time')

        return df

    @staticmethod
    def _get_milliseconds(hours):
        """
        Converts the given hours to milliseconds.

        Parameters
        ----------
        hours : int or float
            The hours to convert to milliseconds.

        Returns
        -------
        int
            The converted milliseconds.
        """
        return hours * 60 * 60 * 1000


if __name__ == "__main__":
    # Load environment variables from the .env file
    load_dotenv()

    # Retrieve the API key and secret from the environment variables
    API_KEY = os.getenv('API_KEY_BINANCE')
    API_SECRET = os.getenv('API_SECRET_BINANCE')

    data = DataFetcher(API_KEY, API_SECRET)
    # data.list_available_symbols("MAT")
    data.symbol = "MATICUSDT"
    data.fetch_price()
