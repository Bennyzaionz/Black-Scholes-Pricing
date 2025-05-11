import numpy as np
from scipy.stats import norm

def euro_call_price(S:float=100, K:float=100, T:float=1, t:float=0, r:float=0.05, sigma:float=0.05):

    """
    Parameters:

    S : float - current underlying stock price
    K : float - strike price
    T : float - time to maturity in years
    t : float - current time in years (from beginning of contract)
    r : float - interest rate
    sigma : float - volatility

    Returns:

    price : float - call option price
    """

    d1 = (np.log(S / K) + (r + 0.5 * sigma**2) * (T - t)) / (sigma * np.sqrt(T - t))
    d2 = d1 - sigma * np.sqrt(T - t)

    call_price = S * norm.cdf(d1) - K * np.exp(-r * (T - t)) * norm.cdf(d2)

    return call_price

def euro_put_price(S:float=100, K:float=100, T:float=1, t:float=0, r:float=0.05, sigma:float=0.05):

    """
    Parameters:

    S : float - current underlying stock price
    K : float - strike price
    T : float - time to maturity in years
    t : float - current time in years (from beginning of contract)
    r : float - interest rate
    sigma : float - volatility

    Returns:

    price : float - put option price
    """
    # put-call parity
    put_price = euro_call_price(S, K, T, t, r, sigma) - S + K * np.exp(-r * (T - t))

    return put_price