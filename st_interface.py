import streamlit as st
import bisect
import numpy as np
from stock_data import get_bs_parameters, get_option_data
from plots import plot_BS_option_prices, plot_market_option_prices, plot_BS_option_error, plot_greek, plot_pnl
from price_filter import remove_majority_na

# -----wide mode-----
st.set_page_config(layout="wide")

# -----titles-----
st.title("Black-Scholes Option Pricing")

st.info("Compute the **risk neutral** price of call and put options on any stock for "
        "**varying strike prices and expirations** under the **Black-Scholes model**. "
        "Display any of the 5 main **Greeks** for each option, or focus in on a single option. "
        "Enter a ticker symbol and adjust the parameters on the left to get started")

st.markdown("---")

# -----sidebar selections-----

# title

st.sidebar.markdown("## Black-Scholes Model")

st.sidebar.markdown("Created by: Benny Zaionz")

col1, col2 = st.sidebar.columns([1, 1])

# links

with col1:
    st.markdown("""
                <a href="https://www.linkedin.com/in/benjamin-zaionz-792864203/" target="_blank">
                    <img src="https://cdn-icons-png.flaticon.com/512/174/174857.png" width="50" alt="LinkedIn">
                </a>
                """, unsafe_allow_html=True)
with col2:
    st.markdown("""
                <a href="https://github.com/Bennyzaionz" target="_blank">
                    <img src="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png" width="50" alt="github">
                </a>
                """, unsafe_allow_html=True)
    
st.sidebar.markdown("---")

# pricing settings

st.sidebar.markdown("### Pricing Settings")

st.sidebar.text_input('Ticker Symbol:', key='ticker', value='AAPL')

volatility_method = st.sidebar.selectbox('Method to Compute Volatility:', ['std', 'log', 'ewma', 'log ewma'])

r, sigma, S = get_bs_parameters(ticker=st.session_state.ticker, volatility_method=volatility_method, output=False)

valid_input = False if r == -1 else True

# -----write rest of objects to screen-----

if valid_input:

    # -----continue sidebar-----

    # get market option price data
    live_call_prices, live_put_prices, strikes, expirations = get_option_data(st.session_state.ticker)
    num_expirations = len(expirations)
    num_strikes = len(strikes)

    exp_value = (expirations[0], expirations[-1]) if len(expirations) < 7 else (expirations[0], expirations[6])

    # print("length:", len(expirations))
    # print(expirations)

    # if len(expirations) < 5:
    #     exp_value = (expirations[0], expirations[-1])
    # else:
    #     exp_value = (expirations[0], expirations[5])

    # sliders for expiration and strike
    expiration_min, expiration_max = st.sidebar.select_slider('Range of Expirations', 
                                                              options=expirations, 
                                                              value=exp_value)
    
    # get list of strikes and expirations for plotting
    exp_start_index = expirations.index(expiration_min)
    exp_end_index = expirations.index(expiration_max)
    
    strike_lower_index = bisect.bisect_right(strikes, S) - 1
    
    strike_min, strike_max = st.sidebar.select_slider('Range of Strikes',
                                                      options=strikes,
                                                      value=(strikes[strike_lower_index - 2], strikes[strike_lower_index + 4]))
    
    remove_na = st.sidebar.checkbox("Remove Strikes Without Listed Prices")
    
    strike_start_index = strikes.index(strike_min)
    strike_end_index = strikes.index(strike_max)

    expiration_range = expirations[exp_start_index:exp_end_index]
    strike_range = strikes[strike_start_index:strike_end_index]

    if remove_na:
        market_call_prices, market_put_prices, strike_range = remove_majority_na(live_call_prices, 
                                                                                live_put_prices, 
                                                                                exp_start_index, 
                                                                                exp_end_index, 
                                                                                strike_start_index, 
                                                                                strike_end_index, 
                                                                                strike_range)
    else:
        market_call_prices = live_call_prices[strike_start_index:strike_end_index, exp_start_index:exp_end_index]
        market_put_prices = live_put_prices[strike_start_index:strike_end_index, exp_start_index:exp_end_index]

    # Greeks Settings

    st.sidebar.markdown("---")

    st.sidebar.markdown("### Greeks Settings")

    show_delta = st.sidebar.checkbox("Show Δ")

    show_gamma = st.sidebar.checkbox("Show Γ")

    show_theta = st.sidebar.checkbox("Show Θ")

    show_vega = st.sidebar.checkbox("Show ν")

    show_rho = st.sidebar.checkbox("Show ρ")

    # focus settings

    st.sidebar.markdown("---")

    st.sidebar.markdown("### Single Option View")

    single_view = st.sidebar.checkbox("Enable Single Option View")

    # -----write stock and market data-----
    
    st.markdown("## Pricing")
    st.write(f"Risk-free rate: {r:.4f}")
    st.write(f"Underlying volatility: {sigma:.4f}" )
    st.write(f"Current Price of {st.session_state.ticker}: ${S:.2f}")

    # -----plot theoretical prices-----

    price_fig, call_prices, put_prices = plot_BS_option_prices(S, 0, r, sigma, st.session_state.ticker, strike_range, expiration_range)

    # with st.container(height=600):
    st.pyplot(price_fig)

    # -----plot market prices-----

    # market_call_prices = live_call_prices[strike_start_index:strike_end_index, exp_start_index:exp_end_index]
    # market_put_prices = live_put_prices[strike_start_index:strike_end_index, exp_start_index:exp_end_index]

    market_fig = plot_market_option_prices(market_call_prices, market_put_prices, strike_range, expiration_range, st.session_state.ticker)
    
    st.pyplot(market_fig)

    # -----plot model error-----

    error_fig = plot_BS_option_error(market_call_prices, market_put_prices, call_prices, put_prices, strike_range, expiration_range, st.session_state.ticker)

    st.pyplot(error_fig)

    # continue focus settings

    if single_view:

        K = st.sidebar.select_slider('Strike', options=strike_range)

        T = st.sidebar.select_slider(f"Expiration", options=expiration_range)

        strike_index = strike_range.index(K)

        expiration_index = expiration_range.index(T)

        call_price = call_prices[strike_index][expiration_index]

        put_price = put_prices[strike_index][expiration_index]

    # -----plot greeks-----

    delta_fig, delta_call, delta_put = plot_greek("Delta", S, 0, r, sigma, strike_range, expiration_range, st.session_state.ticker)
    gamma_fig, gamma_call, gamma_put = plot_greek("Gamma", S, 0, r, sigma, strike_range, expiration_range, st.session_state.ticker)
    theta_fig, theta_call, theta_put = plot_greek("Theta", S, 0, r, sigma, strike_range, expiration_range, st.session_state.ticker)
    vega_fig, vega_call, vega_put = plot_greek("Vega", S, 0, r, sigma, strike_range, expiration_range, st.session_state.ticker)
    rho_fig, rho_call, rho_put = plot_greek("Rho", S, 0, r, sigma, strike_range, expiration_range, st.session_state.ticker)

    if show_delta or show_gamma or show_rho or show_theta or show_vega:
        st.markdown("---")
        st.markdown("## The Greeks")

    if show_delta:
        st.pyplot(delta_fig)

    if show_gamma:
        st.pyplot(gamma_fig)

    if show_theta:
        st.pyplot(theta_fig)

    if show_vega:
        st.pyplot(vega_fig)

    if show_rho:
        st.pyplot(rho_fig)

    # Plot PnL

    if single_view:

        st.markdown("---")
        st.markdown("## Single Option View")

        col_call, col_put = st.columns([1, 1])

        with col_call:
            st.markdown("### Call")
            st.write(f"Price: ${call_price:.4f}")
            st.markdown(f"Δ<sub>c</sub> = {delta_call[strike_index][expiration_index]:.4f}", unsafe_allow_html=True)
            st.markdown(f"Γ<sub>c</sub> = {gamma_call[strike_index][expiration_index]:.4f}", unsafe_allow_html=True)
            st.markdown(f"Θ<sub>c</sub> = {theta_call[strike_index][expiration_index]:.4f}", unsafe_allow_html=True)
            st.markdown(f"ν<sub>c</sub> = {vega_call[strike_index][expiration_index]:.4f}", unsafe_allow_html=True)
            st.markdown(f"ρ<sub>c</sub> = {rho_call[strike_index][expiration_index]:.4f}", unsafe_allow_html=True)

        with col_put:
            st.markdown("### Put")
            st.write(f"Price: ${put_price:.4f}")
            st.markdown(f"Δ<sub>c</sub> = {delta_put[strike_index][expiration_index]:.4f}", unsafe_allow_html=True)
            st.markdown(f"Γ<sub>c</sub> = {gamma_put[strike_index][expiration_index]:.4f}", unsafe_allow_html=True)
            st.markdown(f"Θ<sub>c</sub> = {theta_put[strike_index][expiration_index]:.4f}", unsafe_allow_html=True)
            st.markdown(f"ν<sub>c</sub> = {vega_put[strike_index][expiration_index]:.4f}", unsafe_allow_html=True)
            st.markdown(f"ρ<sub>c</sub> = {rho_put[strike_index][expiration_index]:.4f}", unsafe_allow_html=True)

        pnl_fig = plot_pnl(K, T, S, call_price, put_price)
        st.pyplot(pnl_fig)

else:
    st.write('ticker does not exist')
