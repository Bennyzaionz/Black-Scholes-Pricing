import yfinance as yf
import datetime as dt
import pandas as pd
from volatility_methods import compute_std_dev, compute_ewma_volatility

def ticker_exists(ticker_symbol):

    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info
    except:
        return False
        raise NameError(f"----------Ticker {ticker_symbol} does not exist----------")
    return True  

def get_stock_data(ticker:str, start_date:dt.datetime):
    """
    returns pandas dataframe with Close, High, Low, Open, and Volume columns if ticker exists
    returns empty dataframe if ticker does not exist
    """

    end_date = dt.datetime.today()

    if not ticker_exists(ticker):
        print(f"\n{ticker} is not a valid ticker symbol, please try again")
        return pd.DataFrame()

    print(f"Starting download for {ticker}...\n")

    stock_data = yf.download(ticker, start_date, end_date, auto_adjust=True, ) if ticker_exists(ticker) else None

    print(f"\nFinished downloading\n")

    return stock_data

def get_volatility(stock_data:pd.DataFrame, method:str="log"):
    """
    returns best estimate for Black-Scholes volatility (i.e constant over time)
    methods: log, std, ewma, log ewma, garch, log garch
    """
    
    print(f"Computing volatility based on {method} method\n")

    if method == "std":
        return compute_std_dev(stock_data, "std")
    elif method == "log":
        return compute_std_dev(stock_data, "log")
    elif method == "ewma":
        return compute_ewma_volatility(stock_data, "std")
    elif method == "log ewma":
        return compute_ewma_volatility(stock_data, "log")
    elif method == "garch":
        return compute_garch_volatility(stock_data, "std")
    elif method == "log garch":
        return compute_garch_volatility(stock_data, "std")

    return -1

def get_risk_free_rate():
    """
    returns the risk free rate obtained from 3-month US t-bill
    """
    t_bill = yf.Ticker("^IRX")

    print("Retrieving risk free rate from 3-month US t-bill\n")

    rate = t_bill.history(period="1d")["Close"].iloc[-1]

    return rate / 100  # Convert from percent to decimal

def get_current_price(stock_data, ticker):

    print(f"Retreiving current price of {ticker}\n")

    current_price = stock_data['Close'].to_numpy()[0][-1]

    return current_price

def get_bs_parameters(ticker:str='AAPL', volatility_method:str='log', time:int=1, output:bool=True):
    """
    Parameters:
    ticker : str - ticker symbol for stock
    volatility_method : str - method to compute volatility (methods: log, std, ewma, log ewma, garch, log garch)
    time : int - time in history to compute volatility in years (ex. time=1, voltatility is computed from 1 yr of historical data)

    Returns:
    r : float - risk free rate (obtained from 3-month US t-bills)
    sigma : float - volatility 
    S : float - current price of underlying (ticker)
    """

    start_date = dt.datetime.today() - dt.timedelta(days=365)

    stock_data = get_stock_data(ticker=ticker, start_date=start_date)

    if stock_data.empty:

        return -1, -1, -1

    r = get_risk_free_rate()

    sigma = get_volatility(stock_data=stock_data, method=volatility_method)

    S = get_current_price(stock_data=stock_data, ticker=ticker)

    if output:
        print(f"r: {r:.4f}, sigma: {sigma:.4f}, S: {S:.2f}\n")

    return r, sigma, S

# ticker = "AAPL"

# start_date = dt.datetime.today() - dt.timedelta(days=10)

# aapl_data = get_stock_data(ticker=ticker, start_date=start_date)

# if aapl_data.empty:

#     print("please try again")

# else:

#     print(get_volatility(aapl_data, "std"))

#     print(get_volatility(aapl_data, "log"))

#     print(get_volatility(aapl_data, "ewma"))

#     print(get_volatility(aapl_data, "log ewma"))

# print(get_bs_parameters())

