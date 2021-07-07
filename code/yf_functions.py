# Raw packages
import numpy as np
import pandas as pd
# Data Source
import pandas.core.frame
import yfinance as yf
# Data visualization
import plotly.graph_objs as go
# Other imports
import os
import config as cfg
import configparser
import urllib.request
from datetime import datetime
import time

# Global Variables

SYSTEM_TIME = datetime.now().strftime("%H:%M").split(':')
SYSTEM_TIME = [int(i) for i in SYSTEM_TIME]


# Helper functions

def check_connection(host='https://finance.yahoo.com/'):
    """
    Checks connection status
    :param host: google.com by defualt
    :type host: str
    :return: True if network is available, False if network is unavailable
    :rtype: bool
    """
    try:
        urllib.request.urlopen(host)
        return True
    except:
        return False


def decimal2_float(i: float) -> float:
    """
    Returns float of only 2 decimal length (.xx)
    :param i: a float to be returned without whole decimal numbers
    :type i: float
    :return: only 2 decimal length float
    :rtype: float
    """
    return float("{:.2f}".format(i))


def download_ticker(ticker, dates, interval):
    """
    downloads a ticker as pandas
    :param ticker:
    :type ticker:
    :param dates:
    :type dates:
    :param interval:
    :type interval:
    :return:
    :rtype:
    """
    return yf.download(tickers=ticker, period=dates, interval=interval)


def show_graph(pandas_ticker):
    """
    Shows pandas in a candle graph
    :param pandas_ticker: a pandas
    :type pandas_ticker: pandas.core.frame.Dataframe
    """
    fig = go.Figure()  # Declare on figure
    fig.add_trace(go.Candlestick(x=pandas_ticker.index,
                                 open=pandas_ticker['Open'],
                                 high=pandas_ticker['High'],
                                 low=pandas_ticker['Low'],
                                 close=pandas_ticker['Close'], name='market data'))
    fig.update_layout(title='A title', yaxis_title='Stock Price $')
    fig.update_xaxes(
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list([
                dict(count=15, label='15m', step='minute', stepmode='backward'),
                dict(count=45, label='45m', step='minute', stepmode='backward'),
                dict(count=1, label='HTD', step='hour', stepmode='todate'),
                dict(count=3, label='3h', step='hour', stepmode='backward'),
                dict(step='all')
            ])))
    fig.show()


def get_current_yf_price(ticker: yf.Ticker or pandas.core.frame.DataFrame or str) -> float:
    """
    Returns the current ticker price
    :param ticker: a ticker
    :type ticker: yf.Ticker pandas.core.frame.DataFrame or str
    :return: current price in 2 decimals accuracy
    :rtype: float
    """
    if type(ticker) is str:
        ticker = yf.Ticker(ticker)
    if type(ticker) is yf.Ticker:
        todays_data = ticker.history(period='1d')
        return decimal2_float(todays_data['Close'][0])
    if type(ticker) is pandas.core.frame.DataFrame:
        return decimal2_float(ticker['Close'][len(ticker) - 1])  # try [-1:]


def trading_day_started() -> bool:
    """
    Checks if trading day has started according to Summer IL clock
    :return: true if session has started, else false
    :rtype: bool
    """
    if SYSTEM_TIME[0] > 16:
        return True
    elif SYSTEM_TIME[0] >= 16 and SYSTEM_TIME[1] >= 30:
        return True
    else:
        return False


def load_tickers_from_ini() -> list:
    """
    Load a list of tickers from ini file location config.FILE_PATH['INI']
    :return: List of tickers
    :rtype: list
    """
    config = configparser.ConfigParser()
    config.read(cfg.FILE_PATHS['INI'])
    return config['Tickers']['ticker_list'].split(' ')


def get_gap(ticker: str or yf.Ticker or pandas.core.frame.DataFrame) -> float:
    """
    Function that can get either str or yfinance object and calculate gap.
    GAP is calculated todays_open - yesterday_close
    :param ticker: Ticker name or Ticker object
    :type ticker: str or yf.Ticker or pandas.core.frame.DataFrame
    :return: 2 decimal float of GAP candle
    :rtype: float
    """
    if type(ticker) is str:
        ticker = yf.Ticker(ticker)

    if type(ticker) is yf.Ticker:
        history = ticker.history(period='2d')
        return decimal2_float(history['Open'][1] - history['Close'][0])  # try [-2] - # try [-1]?

    if type(ticker) is pandas.core.frame.DataFrame:
        df = ticker.reset_index()
        return decimal2_float(df['Open'][-1] - df['Close'][-2])


def get_SMA(ticker: yf.Ticker or pandas.core.frame.DataFrame, sma: int) -> float:
    """
    Calculate SMA
    :param ticker: a ticker
    :type ticker: yf.Ticker or pandas.core.frame.DataFrame
    :param sma: sma
    :type sma: int
    :return: SMA
    :rtype: float
    """
    if type(ticker) is yf.Ticker:
        history = ticker.history(period='' + str(sma) + 'd')
        return decimal2_float(history['Close'].mean())
    if type(ticker) is pandas.core.frame.DataFrame:
        df = ticker.reset_index()
        df = df.loc[len(df) - sma:len(df)]
        return decimal2_float(df['Close'].mean())


def get_1st_candle(ticker: yf.Ticker or pandas.core.frame.DataFrame or str, interval='2m') -> float:
    """
    Get 1st candle of the day according to interval, if dataframe is given, ignore interval and use the dataframe's
    :param ticker: Ticker
    :type ticker: yf.Ticker or pandas.core.frame.DataFrame or str
    :param interval: interval in 1m,2m,5m,30m,1h template
    :type interval:str
    :return: 1st candle size according to the interval
    :rtype: float
    """
    if type(ticker) is str:
        ticker = yf.Ticker(ticker)
    if type(ticker) is yf.Ticker:
        history = ticker.history(period='1d', interval=interval)
        return decimal2_float(history['Close'][0] - history['Open'][0])
    if type(ticker) is pandas.core.frame.DataFrame:
        ticker = ticker.reset_index()
        return ticker['Close'][0] - ticker['Open'][0]  #


def get_last_day_percentage(ticker: yf.Ticker or pandas.core.frame.DataFrame) -> float:
    """
    Get the last day of trading's percentage change
    :param ticker: a ticker
    :type ticker: yf.Ticker or pandas.core.frame.DataFrame
    :return: percentage as float
    :rtype: float
    """
    # There are two cases: -% and +%
    # need to check if we're during the day or no (up period to 3d and calculate [1] & [2]
    # validate!!!
    period = 3 if SYSTEM_TIME[0] > 16 and SYSTEM_TIME[1] >= 30 else 2
    # ^^ basically, if current time is >16:30 take period of 3d thus getting yesterday's daily change and not today's
    if type(ticker) is yf.Ticker:
        history = ticker.history(period=str(period) + 'd')
        if history['Close'][1] >= history['Close'][0]:
            return decimal2_float(((history['Close'][1] / history['Close'][0]) - 1) * 100)
        else:
            return -decimal2_float((1 - history['Close'][1] / history['Close'][0]) * 100)
    if type(ticker) is pandas.core.frame.DataFrame:
        df = ticker.reset_index()
        start_value = len(df) - period
        end_value = len(df) - 1
        df = df.loc[start_value:end_value]
        if df['Close'][end_value] >= df['Close'][start_value]:
            return decimal2_float(((df['Close'][end_value] / df['Close'][start_value]) - 1) * 100)
        else:
            return -decimal2_float(((df['Close'][end_value] / df['Close'][start_value]) - 1) * 100)


# Shaked's Strategy

def dumb_risk_analysis() -> dict:
    """
    User input is required - RISK CANDLE, RISK$ and TICKER
    :return: Intersting information based on the input
    :rtype: dict
    """
    ticker = input("Insert a ticker: ")
    risk_candle = get_gap(ticker)
    risk = float(input("Enter risk in $: "))
    print(f'Ticker: {ticker}, Gap: {risk_candle}, Risk: {risk}')
    return risk_dict(risk, risk_candle, get_current_yf_price(yf.Ticker(ticker)))


def risk_dict(risk: float, risk_candle: float, current_stock_price: float) -> dict:
    """
    Gets basic information and creates a dictionary with all relevant information.
    RISK_CANDLE
    RISK
    RISK/RISK_CANDLE
    CURRENT_PRICE
    TRANSACTION_SIZE
    PROFIT*1, PROFIT*2, PROFIT*3
    :param risk: risk in dollars
    :type risk: float
    :param risk_candle: gap change/risk candle
    :type risk_candle: float
    :param current_stock_price: current stock price
    :type current_stock_price: float
    :return: dictionary with all relevant information
    :rtype: dict
    """
    short_long = 'LONG'
    if risk_candle < 0:
        short_long = 'SHORT'
    dict_return = {'RISK/RISK_CANDLE': abs(decimal2_float(risk / risk_candle)),
                   'RISK_CANDLE': abs(risk_candle),
                   'RISK': risk,
                   'SHORT/LONG': short_long,
                   'CURRENT_PRICE': None
                   }

    if current_stock_price is not None:
        dict_return |= {
            'TRANSACTION_SIZE': abs(decimal2_float(dict_return['RISK/RISK_CANDLE'] * current_stock_price)),
            'CURRENT_PRICE': abs(decimal2_float(current_stock_price)),
            'PROFIT*1': abs(decimal2_float(current_stock_price + risk_candle)),
            'PROFIT*2': abs(decimal2_float(current_stock_price + (risk_candle * 2))),
            'PROFIT*3': abs(decimal2_float(current_stock_price + (risk_candle * 3)))
        }
        dict_return |= {'STOP_LOSS': abs(decimal2_float(dict_return['CURRENT_PRICE'] - dict_return['RISK_CANDLE']))}
    return dict_return


def risk_analysis(ticker: yf.Ticker or str, risk: float or int) -> dict:
    """
    risk analysis without user input
    :param ticker: ticker
    :type ticker: yf.Ticker or str
    :param risk: risk input by the user
    :type risk: float or int
    :return: all relevant information of received ticker
    :rtype: dict
    """
    gap = get_gap(ticker)
    if trading_day_started():
        gap = get_1st_candle(ticker, interval='2m')
    if type(ticker) is not yf.Ticker:
        ticker = yf.Ticker(ticker)
    return risk_dict(risk, gap, get_current_yf_price(ticker))


def dumb_risk_analysis_tostring(risk_dict: dict, colored=False) -> str:
    """
    This method returns a string with the following information:
    Amount of shares to buy, risk, total cost, suggested stop loss, gain limits 2x-4x.
    :param risk_dict: dictionary returned by dumb_risk_analysis method
    :type risk_dict: dict
    :return: A string of information based on the dict received
    :rtype:str
    """

    class Style:
        BLACK = '\033[30m'
        RED = '\033[31m'
        GREEN = '\033[32m'
        GREEN2 = '\33[92m'
        YELLOW = '\033[33m'
        BLUE = '\033[34m'
        MAGENTA = '\033[35m'
        CYAN = '\033[36m'
        WHITE = '\033[37m'
        UNDERLINE = '\033[4m'
        END = '\33[0m'
        BOLD = '\33[1m'
        ITALIC = '\33[3m'
        CURL = '\33[4m'
        BLINK = '\33[5m'
        BLINK2 = '\33[6m'
        SELECTED = '\33[7m'
        RESET = '\033[0m'

    os.system("")
    if colored:
        if risk_dict['CURRENT_PRICE'] is not None:
            return (
                    f"You'll need to buy "
                    + Style.YELLOW + f"{risk_dict['RISK/RISK_CANDLE']}" + Style.END +
                    f" shares "
                    + Style.YELLOW + f"@{risk_dict['CURRENT_PRICE']}$" + Style.END +
                    f" in the total cost of "
                    + Style.YELLOW + f"@{risk_dict['TRANSACTION_SIZE']}$ " + Style.END
                    + Style.RED + f"\nStop loss @{risk_dict['STOP_LOSS']}" + Style.END
                    + Style.BOLD + f"\nPossible stops:" + Style.END
                    + Style.GREEN + f"\n    Sell in @{risk_dict['PROFIT*1']}$ for a {risk_dict['RISK']}$ gain (x2 the risk) " + Style.END
                    + Style.GREEN + f"\n    Sell in @{risk_dict['PROFIT*2']}$ for a {risk_dict['RISK'] * 2}$ gain (x3 the risk)" + Style.END
                    + Style.GREEN2 + f"\n    Sell in @{risk_dict['PROFIT*3']}$ for a {risk_dict['RISK'] * 3}$ gain (x4 the risk)" + Style.END)
        else:
            return Style.RED + f"Ticker is not valid, but buy: {risk_dict['RISK/RISK_CANDLE']} shares!" + Style.END
    else:
        if risk_dict['CURRENT_PRICE'] is not None:
            return (
                f"You'll need to buy "
                f"{risk_dict['RISK/RISK_CANDLE']}"
                f" shares "
                f"@{risk_dict['CURRENT_PRICE']}$"
                f" in the total cost of "
                f"@{risk_dict['TRANSACTION_SIZE']}$ "
                f"\nStop loss @{risk_dict['STOP_LOSS']}"
                f"\nPossible stops:"
                f"\n    Sell in @{risk_dict['PROFIT*1']}$ for a {risk_dict['RISK']}$ gain (x2 the risk) "
                f"\n    Sell in @{risk_dict['PROFIT*2']}$ for a {risk_dict['RISK'] * 2}$ gain (x3 the risk)"
                f"\n    Sell in @{risk_dict['PROFIT*3']}$ for a {risk_dict['RISK'] * 3}$ gain (x4 the risk)")
        else:
            return f"Ticker is not valid, but buy: {risk_dict['RISK/RISK_CANDLE']} shares!"


# Consolidation Pattern Strategy:

def is_consolidating(df: pandas.core.frame.DataFrame, percentage=2.5, look_back_data=15) -> bool:
    """
    Checks if a ticker is in a consolidation state relative to the given percentage parameter
    By Part Time Larry - Finding Breakout Candidates with Python and Pandas
    :param look_back_data: how many days to look back on (+1) default is 15 (14 days)
    :type look_back_data: int
    :param df: Dataframe
    :type df: pandas.core.frame.DataFrame
    :param percentage: percentage consolidation pattern default is 2.5
    :type percentage: float
    :return: if ticker is in consolidation pattern
    :rtype: bool
    """
    recent_candlesticks = df[-look_back_data:]  # Takes the last two weeks of data
    max_close = recent_candlesticks['Close'].max()  # finds min of close price df
    min_close = recent_candlesticks['Close'].min()  # find max of close price df
    threshold = 1 - (percentage / 100)
    if min_close > (max_close * threshold):
        return True
    return False


def is_breaking_consolidation(df: pandas.core.frame.DataFrame, percentage=2.5, look_back_data=15) -> bool:
    """
    Checks if a ticker is breaking out from consolidation state relative to the given percentage parameter
    By Part Time Larry - Finding Breakout Candidates with Python and Pandas
    :param look_back_data: how many days to look back on (+1) default is 15 (14 days)
    :type look_back_data: int
    :param df: Dataframe
    :type df: pandas.core.frame.DataFrame
    :param percentage: percentage consolidation pattern default is 2.5
    :type percentage: float
    :return:
    :rtype:
    """
    last_close = df[-1:]['Close'].values[0]  # Last close value
    if is_consolidating(df[:-1], percentage=percentage, look_back_data=look_back_data):
        # df[:-1] will go to up to but exclude last day (last_close)
        # Basically all the data but the last row.
        recent_closes = df[-look_back_data:-1]
        if last_close > recent_closes['Close'].max():
            return True
    return False


if __name__ == "__main__":
    if check_connection():
        print("~~~~Connection is good!~~~~")
    else:
        print("~~~~Connection is bad!~~~~\nCrash incoming:")
    ticker = input("Insert Ticker: ")
    # Downloading and showing a ticker on a graph
    risk = input("Insert wanted risk: ")
    ticker_data_5m = download_ticker(ticker, '1d', '5m')
    ticker_data_1d = download_ticker(ticker, '365d', '1d')
    print("----------------------")
    ticker = yf.Ticker(ticker)
    risk_answer = risk_analysis(ticker, int(risk))
    if not trading_day_started():
        print("\033[93mRisk candle is based on GAP since data on the first candle of the day is unavailable.\033[0m")
    print(dumb_risk_analysis_tostring(risk_answer))
    sma = [20, 50, 100, 200]
    for i in sma:
        time.sleep(0.5)
        print(f'SMA {str(i)}: {get_SMA(ticker_data_1d, i)}')
    print(f'Last day of trading change: {get_last_day_percentage(ticker)}%')
    print("----------------------")
    # user_graph = input("Press Y to show graph")
    # if user_graph == 'Y' or user_graph == 'y':
    #     show_graph(ticker_data)

    # print(ticker.history(period='5d'))
    # print(load_tickers_from_ini())
