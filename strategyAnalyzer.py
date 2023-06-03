import ta
import numpy as np
import pandas as pd
#pd.set_option('display.max_rows', 500)


class TradingStrategy:
    def __init__(self, df, initial_cash=10000):
        self.df = pd.to_numeric(df['close_price']).copy()
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.previous_holdings = 0.0
        self.previous_order = None
        self.df['holdings'] = 0.0
        self.df['portfolio_value'] = 0.0

    def calculate_RSI(self, lower_band=30, upper_band=70, lag=0):
        # Calculate RSI
        self.df[f'RSI_{lower_band}_{upper_band}_{lag}'] = ta.momentum.rsi(
            self.df['close_price'], window=lag)
        # Create empty "signals" column
        self.df[f'signal_RSI_{lower_band}_{upper_band}_{lag}'] = 0
        # Generate trading signals based on RSI
        self.df.loc[(
            self.df[f'RSI_{lower_band}_{upper_band}_{lag}'] < 30), f'signal_RSI_{lower_band}_{upper_band}_{lag}'] = -1
        self.df.loc[(
            self.df[f'RSI_{lower_band}_{upper_band}_{lag}'] > 70), f'signal_RSI_{lower_band}_{upper_band}_{lag}'] = 1

    def calculate_portfolio_value(self, strategy_signal):

        # Go through each day
        for i in self.df.index:
            # At each 'Buy' signal, buy as much as you can
            if self.df.at[i, strategy_signal] == 1 and self.previous_order != 1 and self.previous_holdings == 0:
                self.df.at[i, 'holdings'] = self.cash / \
                    self.df.at[i, 'close_price']
                self.cash = 0  # use all cash to buy

            # At each 'Sell' signal, sell everything
            elif self.df.at[i, strategy_signal] == -1:
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
            self.previous_order = self.df.at[i, strategy_signal]

        def print_stats(self):
            # Calculate final portfolio value
            final_portfolio_value = self.df['Portfolio Value'].dropna(
            ).iloc[-1]
            profit = final_portfolio_value - initial_cash

            # Count the number of trades made
            n_trades = self.df['Order'].count()

            # Calculate stats
            print(self.df)
            print(f'Initial portfolio value: ${initial_cash:.2f}')
            print(f'Final portfolio value: ${final_portfolio_value:.2f}')
            print(f'Profit: ${profit:.2f}')
            print(f'Number of trades made: {n_trades}')


if __name__ == "__main__":
    # Get the data
    dfPrice = pd.read_pickle("MATICUSDT.pkl")
