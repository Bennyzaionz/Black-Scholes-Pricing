Author: Benny Zaionz

Project Description:

Price european call and put options (without divedends) using the Black-Scholes model. 

File Descriptions:
	
	main.py - text based interface for plotting option prices (heatmap for call and put)
	options.py - contains the functions for computing the Black-Scholes price of a european call and put option without divedends
	plots.py - contains the functions for plotting prices of options over various strike prices and expirations on a heatmap
	st_interface.py - containts the GUI using the streamlit.io library
	stock_data.py - contains the functions to compute stock parameters (risk-free rate, volatility, current price) used for computing Black-Scholes prices
	volatility_methods.py - contains functions to compute volatility with different methods (standard, log, ewma, log-ewma)