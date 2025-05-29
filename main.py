from stock_data import get_bs_parameters
# from plots import plot_BS_option_prices, plot_pnl
from options import compute_pnl
import yfinance as yf
import datetime as dt
import numpy as np
from dateutil.relativedelta import relativedelta
from price_filter import remove_majority_na

# Get options chain for a stock (e.g., AAPL)
# ticker = yf.Ticker("AAPL")

# expirations = ticker.options

# print(type(expirations))
# print("Available expirations:", expirations)

# Get calls and puts for a specific expiration
# opt = ticker.option_chain(expirations[0])
# print(opt.calls.head())
# print(opt.puts.head())

# print(opt.calls['strike'])


# today = dt.today()

# a = np.arange(1, 10, 1)

# day = dt.datetime.today() + relativedelta(days=int(a[2]))

# print(day.strftime('%Y-%m-%d'))

arr = np.array([
    [1, 2, np.nan, 4],
    [np.nan, np.nan, np.nan, 5],
    [7, 8, 9, 10],
    [np.nan, np.nan, 3, 4]
])

print(arr)

nan_counts = np.isnan(arr).sum(axis=1)

keep_rows = nan_counts < (arr.shape[1] / 2)

print(arr[keep_rows])