import streamlit as st
from stock_data import get_bs_parameters
from plots import plot_option_prices_fig

# -----wide mode-----
st.set_page_config(layout="wide")

# -----titles-----
st.title("Black-Scholes Option Pricing")

st.info("Compute the **risk neutral** price of call and put options on any stock for "
        "**varying strike prices and expirations** under the **Black-Scholes model**. "
        "Enter a ticker symbol and adjust the parameters on the left to get started")

st.sidebar.markdown("## Black-Scholes Model")

st.sidebar.markdown("Created by: Benny Zaionz")

col1, col2 = st.sidebar.columns([1, 1])

with col1:
    st.markdown("""
                <a href="https://www.linkedin.com/in/benjamin-zaionz-792864203/" target="_blank">
                    <img src="https://cdn-icons-png.flaticon.com/512/174/174857.png" width="50" alt="LinkedIn">
                </a>
                """, unsafe_allow_html=True)
with col2:
    st.markdown("""
                <a href="https://github.com/Bennyzaionz?tab=projects" target="_blank">
                    <img src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png" width="50" alt="github">
                </a>
                """, unsafe_allow_html=True)
    
st.sidebar.markdown("---")

# -----create objects on screen-----

# text inputs
st.sidebar.text_input('Ticker Symbol:', key='ticker', value='AAPL')

# sliders
radius = st.sidebar.slider('Price Radius', 3, 6)

time_horizon = st.sidebar.slider('Time Horizon', 6, 12)

# selectboxes
scale = st.sidebar.selectbox('Time Scale for Expiration:', ['day', 'week', 'month', 'quarter', 'year'])

volatility_method = st.sidebar.selectbox('Method to Compute Volatility:', ['std', 'log', 'ewma', 'log ewma'])

# plots
r, sigma, S = get_bs_parameters(ticker=st.session_state.ticker, volatility_method=volatility_method, output=False)

valid_input = False if r == -1 else True

# -----write objects to screen-----

if valid_input:

    st.write(f"Risk-free rate: {r:.4f}")
    st.write(f"Underlying volatility: {sigma:.4f}" )
    st.write(f"Current Price of {st.session_state.ticker}: ${S:.2f}")

    fig = plot_option_prices_fig(S, 0, r, sigma, scale, time_horizon, radius)

    st.pyplot(fig)

else:
    st.write('ticker does not exist')
