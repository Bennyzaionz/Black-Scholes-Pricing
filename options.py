import numpy as np
from scipy.stats import norm

def BS_d1(S, K, T, t, r, sigma):
    return (np.log(S / K) + (r + 0.5 * sigma**2) * (T - t)) / (sigma * np.sqrt(T - t))

def BS_d2(T, t, sigma, d1):
    return d1 - sigma * np.sqrt(T - t)

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

    d1 = BS_d1(S, K, T, t, r, sigma)
    d2 = BS_d2(T, t, sigma, d1)

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

def compute_call_pnl(K, S, call_price, prices):
    
    pnl = np.maximum(0, prices - K) - call_price

    return pnl

def compute_put_pnl(K, S, put_price, prices):

    pnl = np.maximum(0, K - prices) - put_price

    return pnl

def compute_pnl(K:float=100, S:float=100, call_price:float=0, put_price:float=0):
    """
    Parameters:

    K : float - strike price
    S : float - current underlying stock price
    call_price : float - cost of call option at strike (and expiration)
    put_price : float - cost of put option at strike (and expiration)
    """

    prices = prices = np.arange(0, 2*S + 5, 5)

    call_pnl = compute_call_pnl(K, S, call_price, prices)

    put_pnl = compute_put_pnl(K, S, put_price, prices)

    return prices, call_pnl, put_pnl

def compute_greeks(S:float, K:float, T:float, t:float, r:float, sigma:float):

    """
    Compute all 5 core Black-Scholes Greeks for both call and put options.

    Parameters:
    - S: Current stock price
    - K: Strike price
    - T: Time to maturity (in years)
    - r: Risk-free interest rate (as decimal)
    - sigma: Volatility (as decimal)

    Returns:
    - Dictionary: {'call': {Delta, Gamma, Theta, Vega, Rho}, 'put': {...}}
    """
    d1 = BS_d1(S, K, T, t, r, sigma)
    d2 = BS_d2(T, t, sigma, d1)

    pdf_d1 = norm.pdf(d1)
    cdf_d1 = norm.cdf(d1)
    cdf_d2 = norm.cdf(d2)
    cdf_neg_d1 = norm.cdf(-d1)
    cdf_neg_d2 = norm.cdf(-d2)

    gamma = pdf_d1 / (S * sigma * np.sqrt(T))
    vega = S * pdf_d1 * np.sqrt(T) / 100  # per 1% change in volatility

    call = {
            'Delta': cdf_d1,
            'Gamma': gamma,
            'Theta': (-S * pdf_d1 * sigma / (2 * np.sqrt(T)) - r * K * np.exp(-r * T) * cdf_d2) / 365,
            'Vega': vega,
            'Rho': (K * T * np.exp(-r * T) * cdf_d2) / 100
           }

    put = {
            'Delta': cdf_d1 - 1,
            'Gamma': gamma,
            'Theta': (-S * pdf_d1 * sigma / (2 * np.sqrt(T)) + r * K * np.exp(-r * T) * cdf_neg_d2) / 365,
            'Vega': vega,
            'Rho': (-K * T * np.exp(-r * T) * cdf_neg_d2) / 100
          }

    return {'call': call, 'put': put}