import ta
import datetime
import numpy as np
import pandas as pd
#pd.set_option('display.max_rows', 500)


class TradingStrategy:
    def __init__(self, df, initial_cash=10000):
        self.df = pd.DataFrame(pd.to_numeric(df['close_price']).copy())
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.previous_holdings = 0.0
        self.previous_order = None
        self.df.loc[:, 'holdings'] = 0.0
        self.df.loc[:, 'portfolio_value'] = 0.0
        self.df.loc[:, 'signal_buy_and_hold'] = 1
        self.strategy_signal = 'signal_buy_and_hold'

    def calculate_RSI(self, lower_band=30, upper_band=70, lag=14):
        # Calculate RSI
        self.df[f'RSI_{lower_band}_{upper_band}_{lag}'] = ta.momentum.rsi(
            self.df['close_price'], window=lag)
        # Create empty "signals" column
        self.df[f'signal_RSI_{lower_band}_{upper_band}_{lag}'] = 0
        # Generate trading signals based on RSI
        self.df.loc[(
            self.df[f'RSI_{lower_band}_{upper_band}_{lag}'] < lower_band), f'signal_RSI_{lower_band}_{upper_band}_{lag}'] = -1
        self.df.loc[(
            self.df[f'RSI_{lower_band}_{upper_band}_{lag}'] > upper_band), f'signal_RSI_{lower_band}_{upper_band}_{lag}'] = 1

        self.strategy_signal = f'signal_RSI_{lower_band}_{upper_band}_{lag}'

    def calculate_inverse_RSI(self, lower_band=30, upper_band=70, lag=14):
        # Calculate RSI
        self.df[f'RSI_{lower_band}_{upper_band}_{lag}'] = ta.momentum.rsi(
            self.df['close_price'], window=lag)
        # Create empty "signals" column
        self.df[f'inverse_signal_RSI_{lower_band}_{upper_band}_{lag}'] = 0
        # Generate trading signals based on RSI
        self.df.loc[(
            self.df[f'RSI_{lower_band}_{upper_band}_{lag}'] < lower_band), f'inverse_signal_RSI_{lower_band}_{upper_band}_{lag}'] = 1
        self.df.loc[(
            self.df[f'RSI_{lower_band}_{upper_band}_{lag}'] > upper_band), f'inverse_signal_RSI_{lower_band}_{upper_band}_{lag}'] = -1

        self.strategy_signal = f'inverse_signal_RSI_{lower_band}_{upper_band}_{lag}'

    def calculate_portfolio_value(self):

        # reset parameters
        self.cash = self.initial_cash
        self.previous_holdings = 0.0
        self.previous_order = None
        self.df.loc[:, 'holdings'] = 0.0
        self.df.loc[:, 'portfolio_value'] = 0.0

        # Go through each day
        for i in self.df.index:
            # At each 'Buy' signal, buy as much as you can
            if self.df.at[i, self.strategy_signal] == 1 and self.previous_order != 1 and self.previous_holdings == 0:
                self.df.at[i, 'holdings'] = self.cash / \
                    self.df.at[i, 'close_price']
                self.cash = 0  # use all cash to buy

            # At each 'Sell' signal, sell everything
            elif self.df.at[i, self.strategy_signal] == -1:
                self.cash += self.previous_holdings * \
                    self.df.at[i, 'close_price']
                self.df.at[i, 'holdings'] = 0

            # If there's no signal, holdings are the same as yesterday
            else:
                self.df.at[i, 'holdings'] = self.previous_holdings

            # Calculate portfolio value (cash + holdings * price)
            self.df.at[i, 'portfolio_value'] = self.cash + \
                self.df.at[i, 'holdings'] * self.df.at[i, 'close_price']

            # Update the previous_holdings
            self.previous_holdings = self.df.at[i, 'holdings']

            # Update the previous order for next iteration
            self.previous_order = self.df.at[i, self.strategy_signal]

    def print_stats(self):
        # Calculate final portfolio value
        final_portfolio_value = self.df['portfolio_value'].dropna(
        ).iloc[-1]
        profit = final_portfolio_value - self.initial_cash

        # Count the number of trades made
        n_trades = ((self.df[self.strategy_signal] != 0) & (
            self.df[self.strategy_signal] != self.df[self.strategy_signal].shift(-1))).sum()

        # Calculate stats
        print(f'Strategy: {self.strategy_signal}')
        print(40*'-')
        print(
            f'Start date: {datetime.datetime.fromtimestamp(self.df.index[0]/1000)}')
        print(f'Initial portfolio value: ${self.initial_cash:.2f}')
        print(
            f'Stop date: {datetime.datetime.fromtimestamp(self.df.index[-1]/1000)}')
        print(f'Final portfolio value: ${final_portfolio_value:.2f}')
        print(f'ROI: {(final_portfolio_value/self.initial_cash)*100 - 100:.2f}%')
        print(f'Profit: ${profit:.2f}')
        print(f'Number of trades made: {n_trades}')
        print(40*'-')


if __name__ == "__main__":
    # Get the data
    dfPrice = pd.read_pickle("data/MATICUSDT.pkl")

    tradingAnalyzer = TradingStrategy(dfPrice)
    tradingAnalyzer.calculate_RSI(lag=14)
    tradingAnalyzer.calculate_portfolio_value()
    tradingAnalyzer.print_stats()
