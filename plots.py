import matplotlib.pyplot as plt
import numpy as np
from options import euro_call_price, euro_put_price

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

def plot_matrices(call_prices, put_prices, strike_range, expiration_range, scale, ticker, current_price):

    fig, (ax_call, ax_put) = plt.subplots(1, 2)

    # plot call

    im_call = ax_call.imshow(call_prices, cmap='viridis')

    for (i, strike) in enumerate(strike_range):
        for (j, expiration) in enumerate(expiration_range):

            # between 0 and 1, coefficient reps the percentage of range (min - max) that the text is white for
            a = 0.85

            # set dynamic threshold for color of text (display dark text on light background and visa versa)
            thresh = (1 - a) * np.min(call_prices) + a * np.max(call_prices)

            color = 'white' if call_prices[i][j] < thresh else 'black'

            ax_call.text(j, i, f"{call_prices[i][j]:.2f}", ha='center', va='center', color=color)
    
    ax_call.set_xticks(ticks=range(call_prices.shape[1]), labels=np.arange(1, call_prices.shape[1] + 1, 1))
    ax_call.set_yticks(ticks=range(call_prices.shape[0]), labels=strike_range)
    ax_call.invert_yaxis()
    ax_call.set_xlabel(f"Expiration ({scale}s)")
    ax_call.set_ylabel(f"Strike ($)")
    ax_call.set_title(f"Call Option Prices for {ticker}, current price = {current_price:.2f}")

    # plot put

    im_put = ax_put.imshow(put_prices, cmap='viridis')

    for (i, strike) in enumerate(strike_range):
        for (j, expiration) in enumerate(expiration_range):

            # set dynamic threshold for color of text (display dark text on light background and visa versa)
            thresh = (1 - a) * np.min(put_prices) + a * np.max(put_prices)

            color = 'white' if put_prices[i][j] < thresh else 'black'

            ax_put.text(j, i, f"{put_prices[i][j]:.2f}", ha='center', va='center', color=color)
    
    ax_put.set_xticks(ticks=range(put_prices.shape[1]), labels=np.arange(1, put_prices.shape[1] + 1, 1))
    ax_put.set_yticks(ticks=range(put_prices.shape[0]), labels=strike_range)
    ax_put.invert_yaxis()
    ax_put.set_xlabel(f"Expiration ({scale}s)")
    ax_put.set_ylabel(f"Strike ($)")
    ax_put.set_title(f"Put Option Prices for {ticker}, current price = {current_price:.2f}")

    # fig.colorbar(im, ax=axes.ravel().tolist())

    plt.show()

    return

def get_matrices_fig(call_prices, put_prices, strike_range, expiration_range, scale):

    height = 9

    width = 2*height

    colorbar_height = 0.72
    
    # fig_call, ax_call = plt.subplots(figsize=(height, width))

    fig, (ax_call, ax_put) = plt.subplots(1, 2, figsize=(width, height))

    # plot call

    im_call = ax_call.imshow(call_prices, cmap='viridis')

    for (i, strike) in enumerate(strike_range):
        for (j, expiration) in enumerate(expiration_range):

            # between 0 and 1, coefficient reps the percentage of range (min - max) that the text is white for
            a = 0.85

            # set dynamic threshold for color of text (display dark text on light background and visa versa)
            thresh = (1 - a) * np.min(call_prices) + a * np.max(call_prices)

            color = 'white' if call_prices[i][j] < thresh else 'black'

            ax_call.text(j, i, f"{call_prices[i][j]:.2f}", ha='center', va='center', color=color)
    
    ax_call.set_xticks(ticks=range(call_prices.shape[1]), labels=np.arange(1, call_prices.shape[1] + 1, 1))
    ax_call.set_yticks(ticks=range(call_prices.shape[0]), labels=strike_range)
    ax_call.invert_yaxis()
    ax_call.set_xlabel(f"Expiration ({scale}s)")
    ax_call.set_ylabel(f"Strike ($)")
    ax_call.set_title(f"Call Option Prices")

    fig.colorbar(im_call, shrink=colorbar_height)

    # plot put

    # fig_put, ax_put = plt.subplots(figsize=(height, width))

    im_put = ax_put.imshow(put_prices, cmap='viridis')

    for (i, strike) in enumerate(strike_range):
        for (j, expiration) in enumerate(expiration_range):

            # set dynamic threshold for color of text (display dark text on light background and visa versa)
            thresh = (1 - a) * np.min(put_prices) + a * np.max(put_prices)

            color = 'white' if put_prices[i][j] < thresh else 'black'

            ax_put.text(j, i, f"{put_prices[i][j]:.2f}", ha='center', va='center', color=color)
    
    ax_put.set_xticks(ticks=range(put_prices.shape[1]), labels=np.arange(1, put_prices.shape[1] + 1, 1))
    ax_put.set_yticks(ticks=range(put_prices.shape[0]), labels=strike_range)
    ax_put.invert_yaxis()
    ax_put.set_xlabel(f"Expiration ({scale}s)")
    ax_put.set_ylabel(f"Strike ($)")
    ax_put.set_title(f"Put Option Prices")

    fig.colorbar(im_put, shrink=colorbar_height)

    return fig

def plot_option_prices(S:float=100, t:float=0, r:float=0.05, sigma:float=0.05, scale:str="month", length:int=6, radius:int=3, ticker:str="STOCK"):

    strike_range = compute_strike_range(S, radius)

    expiration_range, scale = compute_expiration_range(scale, length)

    call_prices, put_prices = compute_option_prices(strike_range, expiration_range, S, t, r, sigma)

    plot_matrices(call_prices, put_prices, strike_range, expiration_range, scale, ticker, S)

    return

def plot_option_prices_fig(S:float=100, t:float=0, r:float=0.05, sigma:float=0.05, scale:str="month", length:int=6, radius:int=3):
    
    strike_range = compute_strike_range(S, radius)

    expiration_range, scale = compute_expiration_range(scale, length)

    call_prices, put_prices = compute_option_prices(strike_range, expiration_range, S, t, r, sigma)

    fig = get_matrices_fig(call_prices, put_prices, strike_range, expiration_range, scale)

    return fig
    
