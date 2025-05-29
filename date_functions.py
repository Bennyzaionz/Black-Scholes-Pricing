import datetime as dt
import streamlit as st

@st.cache_data
def str_date_to_years(expiration_range:str):

    """
    converts a date format from str to number of years until that date
    """

    expiration_years = []

    for exp in expiration_range:

        exp_date = dt.datetime.strptime(exp, "%Y-%m-%d")

        today = dt.datetime.combine(dt.date.today(), dt.time.min)

        delta = (exp_date - today).days / 365.25
        
        expiration_years.append(delta)
    
    return expiration_years