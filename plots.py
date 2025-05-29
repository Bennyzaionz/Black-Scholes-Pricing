import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
# import datetime as dt
# from dateutil.relativedelta import relativedelta
from options import compute_pnl, compute_option_prices, compute_greek_matrices
from date_functions import str_date_to_years

# def compute_strike_range(S:float=100, radius:float=3):
    
#     # rule obtained from the OCC: https://www.theocc.com/clearance-and-settlement/clearing/equity-options-product-specifications
#     if S < 25:
#         increment = 2.5
#     elif S < 200:
#         increment = 5
#     else:
#         increment = 10

#     # compute centre rounded up and down to nearest increment
#     centre_floor = np.floor(S / increment) * increment
#     centre_ceil = np.ceil(S / increment) * increment

#     # edge case when current stock price is divisible by increment
#     if centre_floor == centre_ceil:
#         centre_floor = centre_ceil - increment

#     # compute min and max strike prices (exclusive of max)
#     # min is radius - 1 becuase it includes centre_floor
#     min = centre_floor - increment * (radius - 1)
#     max = centre_ceil + increment * radius

#     range = np.arange(min, max, increment)

#     return range

# def compute_expiration_range(scale:str="month", length:float=6):
#     """
#     Parameters:

#     scale : str - scale of time for expiration range (day, week, month, quarter, year)
#     """

#     scales = ["day", "week", "month", "quarter", "year"]
#     divisors = [365, 52, 12, 3, 1]

#     if scale in scales:
#         index = [i for (i, val) in enumerate(scales) if val == scale][0]
#         h = divisors[index]
#     else:
#         print(f"Requested scale does not match existing options {scales} \ndisplaying monthly prices...")
#         h = 12
#         scale = "month"

#     return np.arange(1, length + 1, 1) / h, scale

# def delta_time(scale, num):

#     if scale == 'day': return relativedelta(days=num)

#     elif scale == 'week': return relativedelta(days=num*7)

#     elif scale == 'month': return relativedelta(months=num)

#     elif scale == 'quarter': return relativedelta(months=num*4)

#     return relativedelta(years=num)

def text_color(matrix, value, a):
    
    # between 0 and 1, coefficient reps the percentage of range (min - max) that the text is white for
    # a = 0.8

    # set dynamic threshold for color of text (display dark text on light background and visa versa)
    thresh = (1 - a) * np.nanmin(matrix) + a * np.nanmax(matrix)
    color = 'white' if value < thresh else 'black'

    return color

def get_option_matrices_heatmap_fig(call_matrix, put_matrix, strike_range, expiration_range, call_title, put_title):

    """
    Description:

    general function for plotting heatmaps

    Parameters:

    call_matrix : np.ndarray (2d-array) - call data (ex: price) across strike_range and expiration_range
    put_matrix : np.ndarray (2d-array) - call data (ex: price) across strike_range and expiration_range
    strike_range : np.ndarray - range of strikes in dollars
    expiration_range : np.ndarray - range of expiration dates in scales
    scale : str - [day, week, month, quarter, year]
    call_title : str - title for call plot
    put_title : str - title for put plot

    Returns:

    fig - matplotlib figure with call and put matrices plotted on a heat map with colorbars
    """

    colorbar_height = 0.72

    height = max(len(strike_range), 6)
    width = max(2*len(expiration_range), 12)

    fontsize = 11

    fig, (ax_call, ax_put) = plt.subplots(1, 2, figsize=(width, height))

    # plot call and put prices with heatmap

    # color_scheme = 'PiYG_r'

    colors = ["limegreen", "white", "red"]

    cmap_vibrant = LinearSegmentedColormap.from_list("green_red_vibrant", colors)

    cmap_vibrant = cmap_vibrant.copy()
    cmap_vibrant.set_bad(color='black')

    im_call = ax_call.imshow(call_matrix, cmap=cmap_vibrant)
    im_put = ax_put.imshow(put_matrix, cmap=cmap_vibrant)

    for (i, strike) in enumerate(strike_range):
        for (j, expiration) in enumerate(expiration_range):

            a = 0

            if np.isnan(call_matrix[i][j]):
                ax_call.text(j, i, "Not \nAvailable", ha='center', va='center', color='white', fontsize=8)
            else:
                call_color = text_color(call_matrix, call_matrix[i][j], a)
                ax_call.text(j, i, f"{call_matrix[i][j]:.2f}", ha='center', va='center', color=call_color, fontsize=fontsize)

            if np.isnan(put_matrix[i][j]):
                ax_put.text(j, i, "Not \nAvailable", ha='center', va='center', color='white', fontsize=8)
            else:
                put_color = text_color(put_matrix, put_matrix[i][j], a)
                ax_put.text(j, i, f"{put_matrix[i][j]:.2f}", ha='center', va='center', color=put_color, fontsize=fontsize)

    
    # call labels

    ax_call.set_xticks(ticks=range(call_matrix.shape[1]), labels=expiration_range)
    ax_call.set_yticks(ticks=range(call_matrix.shape[0]), labels=strike_range)
    ax_call.tick_params(axis='x', rotation=75)
    ax_call.invert_yaxis()
    ax_call.set_xlabel(f"Expiration Date")
    ax_call.set_ylabel(f"Strike ($)")
    ax_call.set_title(call_title)

    fig.colorbar(im_call, shrink=colorbar_height)

    # put labels
    
    ax_put.set_xticks(ticks=range(put_matrix.shape[1]), labels=expiration_range)
    ax_put.set_yticks(ticks=range(put_matrix.shape[0]), labels=strike_range)
    ax_put.tick_params(axis='x', rotation=75)
    ax_put.invert_yaxis()
    ax_put.set_xlabel(f"Expiration Date")
    ax_put.set_ylabel(f"Strike ($)")
    ax_put.set_title(put_title)

    fig.colorbar(im_put, shrink=colorbar_height)

    return fig

def plot_BS_option_prices(S:float=100, t:float=0, r:float=0.05, sigma:float=0.05, ticker:str='AAPL', strike_range:list=[], expiration_range:list=[]):

    expiration_range_years = str_date_to_years(expiration_range)

    # print(expiration_range_years)
    
    call_prices, put_prices = compute_option_prices(strike_range, expiration_range_years, S, t, r, sigma)

    call_title = f"Black-Scholes Prices for Call Options on {ticker} ($)"

    put_title = f"Black-Scholes Prices for Put Options on {ticker} ($)"

    fig = get_option_matrices_heatmap_fig(call_prices, put_prices, strike_range, expiration_range, call_title, put_title)

    return fig, call_prices, put_prices

def plot_market_option_prices(call_prices, put_prices, strike_range, expiration_range, ticker):
    
    call_title = f"Market Prices for Call Options on {ticker} ($)"

    put_title = f"Market Prices for Put Options on {ticker} ($)"

    fig = get_option_matrices_heatmap_fig(call_prices, put_prices, strike_range, expiration_range, call_title, put_title)

    return fig

def plot_BS_option_error(market_call_prices, market_put_prices, BS_call_prices, BS_put_prices, strike_range, expiration_range, ticker):

    call_error = BS_call_prices - market_call_prices

    put_error = BS_put_prices - market_put_prices

    call_title = f"Model Erorr for Call Options on {ticker} ($)"

    put_title = f"Model Erorr for Put Options on {ticker} ($)"

    fig = get_option_matrices_heatmap_fig(call_error, put_error, strike_range, expiration_range, call_title, put_title)

    return fig

def plot_greek(greek_name:str, S:float, t:float, r:float, sigma:float, strike_range, expiration_range, ticker):

    expiration_range_years = str_date_to_years(expiration_range)
    
    greeks_call, greeks_put = compute_greek_matrices(greek_name, S, r, sigma, strike_range, expiration_range_years)

    call_title = f"{greek_name} for Call Options on {ticker}"

    put_title = f"{greek_name} for Put Options on {ticker}"

    fig = get_option_matrices_heatmap_fig(greeks_call, greeks_put, strike_range, expiration_range, call_title, put_title)

    return fig, greeks_call, greeks_put

def plot_pnl(K:int=100, T:int=1, S:float=100, call_price:float=0, put_price:float=0):

    prices, call_pnl, put_pnl = compute_pnl(K, S, call_price, put_price)

    call_break_even = K + call_price

    put_break_even = K - put_price

    height = 6

    width = 2*height

    fig, (ax_call, ax_put) = plt.subplots(1, 2, figsize=(width, height))

    ax_call.plot(prices, call_pnl, label='PnL') # plot pnl
    ax_call.axvline(call_break_even, label=f"Break-even: {call_break_even:.2f}", ls='--', color='black')
    ax_call.set_xlabel('Underlying Price ($)')
    ax_call.set_ylabel('Profit ($)')
    ax_call.set_title(f"Call Option PnL, K=${K:.2f}, T={T}")
    ax_call.legend()

    ax_put.plot(prices, put_pnl, label='PnL') # plot pnl
    ax_put.axvline(put_break_even, label=f"Break-even: {put_break_even:.2f}", ls='--', color='black')
    ax_put.set_xlabel('Underlying Price ($)')
    ax_put.set_ylabel('Profit ($)')
    ax_put.set_title(f"Put Option PnL, K=${K:.2f}, T={T}")
    ax_put.legend()

    # plt.show()

    return fig