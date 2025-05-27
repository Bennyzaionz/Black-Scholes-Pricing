import yfinance as yf
import datetime as dt
import pandas as pd
import numpy as np
import streamlit as st
from volatility_methods import compute_std_dev, compute_ewma_volatility

@st.cache_data
def ticker_exists(ticker_symbol):

    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info
    except:
        return False
        raise NameError(f"----------Ticker {ticker_symbol} does not exist----------")
    return True  

@st.cache_data
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

@st.cache_data
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

    return -1

@st.cache_data
def get_risk_free_rate():
    """
    returns the risk free rate obtained from 3-month US t-bill
    """
    t_bill = yf.Ticker("^IRX")

    print("Retrieving risk free rate from 3-month US t-bill\n")

    rate = t_bill.history(period="5d")["Close"].iloc[-1]

    return rate / 100  # Convert from percent to decimal

@st.cache_data
def get_current_price(stock_data, ticker):

    print(f"Retreiving current price of {ticker}\n")

    current_price = stock_data['Close'].to_numpy()[0][-1]

    return current_price

# @st.cache_data
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

@st.cache_data
def get_option_data(ticker):
    
    """
    Returns:
    expirations
    call_prices
    put_prices
    """

    # select ticker and get expirations
    underlying = yf.Ticker(ticker)
    expirations = underlying.options

    # initialize dictionary for call and put strikes and prices
    call_data = {}
    put_data = {}
    strikes = {'call': {}, 'put':{}}

    for exp in expirations:

        # get option chain at exp, keep strike and last price
        chain = underlying.option_chain(exp)
        calls = chain.calls[['strike', 'lastPrice']]
        puts = chain.puts[['strike', 'lastPrice']]

        # Keep strikes that exist in both calls and puts for this expiration
        call_strikes = set(calls['strike'])
        put_strikes = set(puts['strike'])

        # strikes = call_strikes & put_strikes
        strikes['call'][exp] = call_strikes
        strikes['put'][exp] = put_strikes

        # store call and put data
        call_data[exp] = calls.set_index('strike')['lastPrice']
        put_data[exp] = puts.set_index('strike')['lastPrice']  

    # get key for longest set of strikes
    call_key = max(strikes['call'], key=len)
    put_key = max(strikes['put'], key=len)

    # get longest set of strikes
    call_strikes = strikes['call'][call_key]
    put_strikes = strikes['put'][put_key]

    # combine them to cover all possible strikes
    combined_strikes = sorted(call_strikes | put_strikes)

    call_prices = np.zeros((len(combined_strikes), len(expirations)))
    put_prices = np.zeros((len(combined_strikes), len(expirations)))

    for i, strike in enumerate(combined_strikes):
        for j, exp in enumerate(expirations):

            call_prices[i][j] = call_data[exp].get(strike, np.nan)
            put_prices[i][j] = put_data[exp].get(strike, np.nan)

    return call_prices, put_prices, combined_strikes, expirations