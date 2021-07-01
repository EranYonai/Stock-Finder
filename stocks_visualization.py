# Raw packages
import numpy as np
import pandas as pd
# Data Source
import yfinance as yf
# Data visualization
import plotly.graph_objs as go
# Other imports
import os
import config as cfg
import configparser
import urllib.request


def check_connection(host='http://google.com'):
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


def get_current_yf_price(yf_ticker: yf.Ticker):
    """
    Returns the current ticker price
    :param yf_ticker: a ticker
    :type yf_ticker: yf.Ticker
    :return: current price in 2 decimals accuracy
    :rtype: float
    """
    if len(yf_ticker.info) > 2:  # is ticker valid?
        todays_data = yf_ticker.history(period='1d')
        return decimal2_float(todays_data['Close'][0])
    return None


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
    dict_return = {'RISK/RISK_CANDLE': decimal2_float(risk / risk_candle),
                   'RISK_CANDLE': risk_candle,
                   'RISK': risk,
                   'CURRENT_PRICE': None
                   }

    if current_stock_price is not None:
        dict_return |= {
            'TRANSACTION_SIZE': decimal2_float(dict_return['RISK/RISK_CANDLE'] * current_stock_price),
            'CURRENT_PRICE': decimal2_float(current_stock_price),
            'PROFIT*1': decimal2_float(current_stock_price + risk_candle),
            'PROFIT*2': decimal2_float(current_stock_price + (risk_candle * 2)),
            'PROFIT*3': decimal2_float(current_stock_price + (risk_candle * 3))
        }
        dict_return |= {'STOP_LOSS': decimal2_float(dict_return['CURRENT_PRICE'] - dict_return['RISK_CANDLE'])}
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
    risk_candle = get_gap(ticker)
    if type(ticker) is not yf.Ticker:
        ticker = yf.Ticker(ticker)
    return risk_dict(risk, risk_candle, get_current_yf_price(ticker))


def dumb_risk_analysis_tostring(risk_dict: dict) -> str:
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
                + Style.GREEN2 + f"\n    Sell in @{risk_dict['PROFIT*2']}$ for a {risk_dict['RISK'] * 2}$ gain (x3 the risk)" + Style.END
                + Style.GREEN + f"\n    Sell in @{risk_dict['PROFIT*3']}$ for a {risk_dict['RISK'] * 3}$ gain (x4 the risk)" + Style.END)
    else:
        return Style.RED + f"Ticker is not valid, but buy: {risk_dict['RISK/RISK_CANDLE']} shares!" + Style.END


def load_tickers_from_ini():
    """
    Load a list of tickers from ini file location config.FILE_PATH['INI']
    :return: List of tickers
    :rtype: list
    """
    config = configparser.ConfigParser()
    config.read(cfg.FILE_PATHS['INI'])
    return config['Tickers']['ticker_list'].split(',')


def get_gap(ticker) -> float:
    """
    Function that can get either str or yfinance object and calculate gap.
    GAP is calculated todays_open - yesterday_close
    :param ticker: Ticker name or Ticker object
    :type ticker: str or yf
    :return: 2 decimal float of GAP candle
    :rtype: float
    """
    if type(ticker) is str:
        ticker = yf.Ticker(ticker)
    history = ticker.history(period='2d')
    return decimal2_float(history['Open'][1] - history['Close'][0])


# Downloading and showing a ticker on a graph
# data = download_ticker('mrna', '2d', '2m')
# show_graph(data)
# print(type(data))
if check_connection():
    print("~~~~Connection is good!~~~~")
else:
    print("~~~~Connection is bad!~~~~")

print("----------------------")
print(dumb_risk_analysis_tostring(dumb_risk_analysis()))
print("----------------------")
# print(load_tickers_from_ini())
