import numpy as np

def remove_majority_na(call_prices, put_prices, exp_start_index, exp_end_index, strike_start_index, strike_end_index, strikes):
    """
    remove rows that have majority na for market call and put prices (will remove from both call and put if only one has too many nas), intended to be used to pass to plotting functions
    """

    call_prices_sliced = call_prices[strike_start_index:strike_end_index, exp_start_index:exp_end_index]
    put_prices_sliced = put_prices[strike_start_index:strike_end_index, exp_start_index:exp_end_index]

    filter_threshold = call_prices_sliced.shape[1] / 2

    nan_counts_call = np.isnan(call_prices_sliced).sum(axis=1)
    nan_counts_put = np.isnan(put_prices_sliced).sum(axis=1)

    valid_rows_call = nan_counts_call <= filter_threshold
    valid_rows_put = nan_counts_put <= filter_threshold

    valid_rows = valid_rows_call & valid_rows_put

    filtered_call_prices = call_prices_sliced[valid_rows]
    filtered_put_prices = call_prices_sliced[valid_rows]

    # print(call_prices_sliced, put_prices_sliced, filtered_call_prices, filtered_put_prices)

    # print(valid_rows)

    strikes = np.array(strikes)

    filtered_strikes = strikes[valid_rows]

    return filtered_call_prices, filtered_put_prices, filtered_strikes.tolist()