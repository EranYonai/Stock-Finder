import pandas.core.frame
import yfinance as yf

import yf_functions

yf_functions.load_tickers_from_ini()

def give_score(ticker: yf.Ticker or str or pandas.core.frame.DataFrame) -> float:
    return sma_score(ticker)*100


def sma_score(ticker_data: pandas.core.frame.DataFrame) -> float:
    # SMA score calculation percentages:
    ABOVE_SMA20 = 0.4
    ABOVE_SMA50 = 0.1
    ABOVE_SMA100 = 0.2
    ABOVE_SMA200 = 0.3
    sma = {}
    score = 0
    for i in [20, 50, 100, 200]:
        sma |= {str(i): yf_functions.get_SMA(ticker_data, i)}
    current_price = yf_functions.get_current_yf_price(ticker_data)

    score += sma_score_helper(current_price, sma['20'], ABOVE_SMA20)
    score += sma_score_helper(current_price, sma['50'], ABOVE_SMA50)
    score += sma_score_helper(current_price, sma['100'], ABOVE_SMA100)
    score += sma_score_helper(current_price, sma['200'], ABOVE_SMA200)
    return score

def sma_score_helper(current_price, sma, sma_weight):
    # SMA 20 BASED SCORE:
    score = 0
    if sma < current_price:
        score += sma_weight
    elif sma == current_price:
        score += sma_weight * 0.8  # Possible point of trend change
    elif sma > current_price:
        change_percent = ((current_price - sma) * current_price) / 100
        if change_percent < 0.01:  # conversion to the uptrend is expected soon
            score += sma_weight * 0.5
        elif change_percent < 0.02:  # conversion to the uptrend is expected soon-1
            score += sma_weight * 0.4
        elif change_percent < 0.05:  # conversion to the uptrend is expected soon-2
            score += sma_weight * 0.3
        elif change_percent < 0.08:  # conversion to the uptrend is expected soon-3
            score += sma_weight * 0.2
        elif change_percent < 0.04:  # conversion to the uptrend is expected soon-4
            score += sma_weight * 0.2
        else:
            score += sma_weight * 0.1
    return score


def gap_score(ticker_data: pandas.core.frame.DataFrame) -> float:
    GAP_WEIGHT = 0.5
    FIRST_CANDLE_WEIGHT = 0.5
    score = 0
    current_price = yf_functions.get_current_yf_price(ticker_data)
    gap = yf_functions.get_gap(ticker_data)
    # gap/current_price = percentage of change (gap's worth)
    first_candle = yf_functions.get_1st_candle(ticker_data)
    # first_candle/current_price = percentage of change (first candle's worth)
    return score


def momentum_score(ticker_data: pandas.core.frame.DataFrame) -> float:
    MOMENTUM = 0.5
    last_day = yf_functions.get_last_day_percentage(ticker_data)
    return last_day



print(yf_functions.load_tickers_from_ini())
score_list = {}
for tick in yf_functions.load_tickers_from_ini():
    score_list |= {tick: give_score(yf.download(tickers=tick, period='365d', interval='1d'))}

print(score_list)
