import matplotlib.pyplot as plt
import numpy as np
import datetime as dt
from dateutil.relativedelta import relativedelta
from options import euro_call_price, euro_put_price, compute_pnl, compute_greeks

def compute_strike_range(S:float=100, radius:float=3):
    
    # rule obtained from the OCC: https://www.theocc.com/clearance-and-settlement/clearing/equity-options-product-specifications
    if S < 25:
        increment = 2.5
    elif S < 200:
        increment = 5
    else:
        increment = 10

    # compute centre rounded up and down to nearest increment
    centre_floor = np.floor(S / increment) * increment
    centre_ceil = np.ceil(S / increment) * increment

    # edge case when current stock price is divisible by increment
    if centre_floor == centre_ceil:
        centre_floor = centre_ceil - increment

    # compute min and max strike prices (exclusive of max)
    # min is radius - 1 becuase it includes centre_floor
    min = centre_floor - increment * (radius - 1)
    max = centre_ceil + increment * radius

    range = np.arange(min, max, increment)

    return range

def compute_expiration_range(scale:str="month", length:float=6):
    """
    Parameters:

    scale : str - scale of time for expiration range (day, week, month, quarter, year)
    """

    scales = ["day", "week", "month", "quarter", "year"]
    divisors = [365, 52, 12, 3, 1]

    if scale in scales:
        index = [i for (i, val) in enumerate(scales) if val == scale][0]
        h = divisors[index]
    else:
        print(f"Requested scale does not match existing options {scales} \ndisplaying monthly prices...")
        h = 12
        scale = "month"

    return np.arange(1, length + 1, 1) / h, scale

def compute_option_prices(strike_range, expiration_range, S, t, r, sigma):

    call_prices = np.zeros((len(strike_range), len(expiration_range)))
    put_prices = np.zeros((len(strike_range), len(expiration_range)))

    for (i, strike) in enumerate(strike_range):
        for (j, expiration) in enumerate(expiration_range):
            call_prices[i][j] = euro_call_price(S, strike, expiration, t, r, sigma)
            put_prices[i][j] = euro_put_price(S, strike, expiration, t, r, sigma)

    return call_prices, put_prices

def delta_time(scale, num):

    if scale == 'day': return relativedelta(days=num)

    elif scale == 'week': return relativedelta(days=num*7)

    elif scale == 'month': return relativedelta(months=num)

    elif scale == 'quarter': return relativedelta(months=num*4)

    return relativedelta(years=num)

def get_option_matrices_heatmap_fig(call_matrix, put_matrix, strike_range, expiration_range, scale, call_title, put_title):

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

    height = 6
    width = 2*height
    colorbar_height = 0.72

    if len(expiration_range) < 9:
        fontsize = 10
    elif len(expiration_range) < 10:
        fontsize = 8
    else:
        fontsize = 6

    fig, (ax_call, ax_put) = plt.subplots(1, 2, figsize=(width, height))

    # plot call and put prices with heatmap

    color_scheme = 'plasma'
    im_call = ax_call.imshow(call_matrix, cmap=color_scheme)
    im_put = ax_put.imshow(put_matrix, cmap=color_scheme)

    for (i, strike) in enumerate(strike_range):
        for (j, expiration) in enumerate(expiration_range):

            # between 0 and 1, coefficient reps the percentage of range (min - max) that the text is white for
            a = 0.85

            # set dynamic threshold for color of text (display dark text on light background and visa versa)
            thresh = (1 - a) * np.min(call_matrix) + a * np.max(call_matrix)
            color = 'white' if call_matrix[i][j] < thresh else 'black'

            ax_call.text(j, i, f"{call_matrix[i][j]:.2f}", ha='center', va='center', color=color, fontsize=fontsize)

            # set dynamic threshold for color of text (display dark text on light background and visa versa)
            thresh = (1 - a) * np.min(put_matrix) + a * np.max(put_matrix)
            color = 'white' if put_matrix[i][j] < thresh else 'black'

            ax_put.text(j, i, f"{put_matrix[i][j]:.2f}", ha='center', va='center', color=color, fontsize=fontsize)

    # convert strike range to dates

    dates = np.zeros(expiration_range.shape, dtype=object)

    expiration_indeces = np.arange(1, len(expiration_range) + 1)

    for i, num in enumerate(expiration_indeces):
        tmp = dt.datetime.today() + delta_time(scale, int(num))
        # print(tmp.strftime('%Y-%m-%d'), num, scale)
        dates[i] = tmp.strftime('%Y-%m-%d')
    
    # call labels

    ax_call.set_xticks(ticks=range(call_matrix.shape[1]), labels=dates)
    ax_call.set_yticks(ticks=range(call_matrix.shape[0]), labels=strike_range)
    ax_call.tick_params(axis='x', rotation=75)
    ax_call.invert_yaxis()
    ax_call.set_xlabel(f"Expiration Date")
    ax_call.set_ylabel(f"Strike ($)")
    ax_call.set_title(call_title)

    fig.colorbar(im_call, shrink=colorbar_height)

    # put labels
    
    ax_put.set_xticks(ticks=range(put_matrix.shape[1]), labels=dates)
    ax_put.set_yticks(ticks=range(put_matrix.shape[0]), labels=strike_range)
    ax_put.tick_params(axis='x', rotation=75)
    ax_put.invert_yaxis()
    ax_put.set_xlabel(f"Expiration Date")
    ax_put.set_ylabel(f"Strike ($)")
    ax_put.set_title(put_title)

    fig.colorbar(im_put, shrink=colorbar_height)

    return fig

def plot_option_prices_fig(S:float=100, t:float=0, r:float=0.05, sigma:float=0.05, scale:str="month", length:int=6, radius:int=3, ticker:str='AAPL'):
    
    strike_range = compute_strike_range(S, radius)

    expiration_range, scale = compute_expiration_range(scale, length)

    call_prices, put_prices = compute_option_prices(strike_range, expiration_range, S, t, r, sigma)

    call_title = f"Call Option Prices on {ticker} ($)"

    put_title = f"Put Option Prices on {ticker} ($)"

    fig = get_option_matrices_heatmap_fig(call_prices, put_prices, strike_range, expiration_range, scale, call_title, put_title)

    return fig, call_prices, put_prices, strike_range, expiration_range

def plot_pnl(K:int=100, T:int=1, scale:str='day', S:float=100, call_price:float=0, put_price:float=0):

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
    ax_call.set_title(f"Call Option PnL, K=${K:.0f}, T={T} {scale}s")
    ax_call.legend()

    ax_put.plot(prices, put_pnl, label='PnL') # plot pnl
    ax_put.axvline(put_break_even, label=f"Break-even: {put_break_even:.2f}", ls='--', color='black')
    ax_put.set_xlabel('Underlying Price ($)')
    ax_put.set_ylabel('Profit ($)')
    ax_put.set_title(f"Put Option PnL, K=${K:.0f}, T={T} {scale}s")
    ax_put.legend()

    # plt.show()

    return fig

def compute_greek_matrices(greek_name, S, r, sigma, strike_range, expiration_range):

    greeks_call = np.zeros((len(strike_range), len(expiration_range)))
    greeks_put = np.zeros((len(strike_range), len(expiration_range)))

    for (i, strike) in enumerate(strike_range):
        for (j, expiration) in enumerate(expiration_range):
            greeks = compute_greeks(S, strike, expiration, 0, r, sigma)
            greeks_call[i][j] = greeks["call"][greek_name]
            greeks_put[i][j] = greeks["put"][greek_name]

    return greeks_call, greeks_put

def plot_greek(greek_name:str, S:float, t:float, r:float, sigma:float, strike_range, expiration_range, scale, ticker):

    greeks_call, greeks_put = compute_greek_matrices(greek_name, S, r, sigma, strike_range, expiration_range)

    call_title = f"{greek_name} for Call Options on {ticker}"

    put_title = f"{greek_name} for Put Options on {ticker}"

    fig = get_option_matrices_heatmap_fig(greeks_call, greeks_put, strike_range, expiration_range, scale, call_title, put_title)

    return fig, greeks_call, greeks_put