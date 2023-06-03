import ta
import numpy as np
import pandas as pd
#pd.set_option('display.max_rows', 500)

# Get the data
dfAll = pd.read_pickle("bitcoin_price.pkl")

# Ensure the 'close_price' column is numeric for calculations
dfAll['close_price'] = pd.to_numeric(dfAll['close_price'])

# Calculate RSI
dfAll['RSI'] = ta.momentum.rsi(dfAll['close_price'])

# Create empty "signals" column
dfAll['Signal'] = np.nan

# Generate trading signals based on RSI
dfAll.loc[(dfAll['RSI'] < 30), 'Signal'] = 'Sell'
dfAll.loc[(dfAll['RSI'] > 70), 'Signal'] = 'Buy'

# Generate trading orders based on signals
dfAll['Order'] = dfAll['Signal'].shift()

# Initialize portfolio and holdings
dfAll['Holdings'] = 0.0
dfAll['Portfolio Value'] = 0.0
initial_cash = cash = 10000  # starting with $10,000
previous_holdings = 0.0
previous_order = None

# Go through each day
for i in dfAll.index:
    # At each 'Buy' signal, buy as much as you can
    if dfAll.at[i, 'Order'] == 'Buy' and previous_order != 'Buy' and previous_holdings == 0:
        dfAll.at[i, 'Holdings'] = cash / dfAll.at[i, 'close_price']
        cash = 0  # use all cash to buy

    # At each 'Sell' signal, sell everything
    elif dfAll.at[i, 'Order'] == 'Sell':
        cash += previous_holdings * dfAll.at[i, 'close_price']
        dfAll.at[i, 'Holdings'] = 0

    # If there's no signal, holdings are the same as yesterday
    else:
        dfAll.at[i, 'Holdings'] = previous_holdings

    # Calculate portfolio value (cash + holdings * price)
    dfAll.at[i, 'Portfolio Value'] = cash + \
        dfAll.at[i, 'Holdings'] * dfAll.at[i, 'close_price']

    # Update the previous_holdings
    previous_holdings = dfAll.at[i, 'Holdings']

    # Update the previous order for next iteration
    previous_order = dfAll.at[i, 'Order']

# Calculate final portfolio value
final_portfolio_value = dfAll['Portfolio Value'].dropna().iloc[-1]
profit = final_portfolio_value - initial_cash

# Count the number of trades made
n_trades = dfAll['Order'].count()

# Calculate stats
print(dfAll)
print(f'Initial portfolio value: ${initial_cash:.2f}')
print(f'Final portfolio value: ${final_portfolio_value:.2f}')
print(f'Profit: ${profit:.2f}')
print(f'Number of trades made: {n_trades}')
