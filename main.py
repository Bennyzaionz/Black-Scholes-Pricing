from stock_data import get_bs_parameters
from plots import plot_option_prices, plot_pnl
from options import compute_pnl

# ticker = 'NVDA'

# scale = "year"

# valid_input = False

# while not valid_input:
    
#     ticker = input("\nPlease input the ticker symbol for a stock you'd like to price options for:\n\n")

#     print(" ")

#     r, sigma, S = get_bs_parameters(ticker=ticker, volatility_method='log ewma')

#     valid_input = False if r == -1 else True

# scale = input("Please input the time scale for the expiration dates you are interested in (day, week, month, quarter, year)\n\n")

# print(" ")

# plot_option_prices(S=S, r=r, sigma=sigma, scale=scale, ticker=ticker, radius=5, length=10)

# prices, call, put = compute_pnl()

plot_pnl(100, 100, 10, 10)