import pandas as pd
import numpy as np
from arch import arch_model

def compute_returns(stock_data, method:str="log"):
    
    # use a new df to avoid changing original stock_data since pd.DataFrame() get passed by reference

    returns_df = pd.DataFrame()

    returns_df['Returns'] = (stock_data['Close'].pct_change() if method == "std" 
                             else np.log(stock_data['Close'] / stock_data['Close'].shift(1))
                            )

    returns = returns_df['Returns'].dropna().to_numpy()
    
    return  returns_df         

def compute_std_dev(stock_data, method:str="log"):

    returns = compute_returns(stock_data, method)

    # print(stock_data)

    daily_volatility = returns['Returns'].dropna().std() #stock_data['Returns'].dropna().std()

    # daily_volatility = np.std(returns)

    annualized_volatility = daily_volatility * np.sqrt(252)

    return annualized_volatility

def compute_ewma_volatility(stock_data, method:str="log"):
    
    returns = compute_returns(stock_data, method)

    lambda_ = 0.94

    ewma_returns = returns["Returns"].dropna().ewm(span=(2/(1-lambda_)-1))

    # print(ewma_returns)

    daily_volatility = ewma_returns.std().iloc[-1] # returns["Returns"].dropna().ewm(span=(2/(1-lambda_)-1)).std()

    # print(daily_volatility)

    annualized_volatility = daily_volatility * np.sqrt(252)

    return annualized_volatility

def compute_garch_volatility(stock_data, method:str="log"):

    returns = compute_returns(stock_data, method)

    # multiply by 100 for garch model performance, divide again later
    model = arch_model(returns["Returns"].dropna(), vol='Garch', p=1, q=1)
    res = model.fit(disp="off")
    forecast = res.forecast(horizon=5)
    vol_forecast = np.sqrt(forecast.variance.iloc[-1].values[0])

    return vol_forecast

    # return annualized_volatility