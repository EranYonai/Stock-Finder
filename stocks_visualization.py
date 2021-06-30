# Raw packages
import numpy as np
import pandas as pd
# Data Source
import yfinance as yf
# Data visualization
import plotly.graph_objs as go
# Other imports
import os


def download_ticker(ticker, dates, interval):
    return yf.download(tickers=ticker, period=dates, interval=interval)


def show_graph(yfinance_single_ticker):
    fig = go.Figure()  # Declare on figure
    fig.add_trace(go.Candlestick(x=yfinance_single_ticker.index,
                                 open=yfinance_single_ticker['Open'],
                                 high=yfinance_single_ticker['High'],
                                 low=yfinance_single_ticker['Low'],
                                 close=yfinance_single_ticker['Close'], name='market data'))
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


# Downloading and showing a ticker on a graph
# data = download_ticker('aapl', '1d', '2m')
# show_graph(data)

def get_current_yf_price(yf_ticker):
    if len(yf_ticker.info) > 2:  # is ticker valid?
        todays_data = yf_ticker.history(period='1d')
        return todays_data['Close'][0]
    return None


def dumb_risk_analysis():
    risk_candle = float(input("Enter risk candle value in $: "))
    risk = float(input("Enter risk in $: "))
    ticker = input("On which Ticker? ")
    user_ticker = yf.Ticker(ticker)
    current_stock_price = get_current_yf_price(user_ticker)
    dict_return = {'RISK/RISK_CANDLE': risk / risk_candle,
                   'RISK_CANDLE': risk_candle,
                   'RISK': risk,
                   'CURRENT_PRICE': None
                   }

    if current_stock_price is not None:
        dict_return |= {
            'TRANSACTION_SIZE': float("{:.2f}".format(dict_return['RISK/RISK_CANDLE'] * current_stock_price)),
            'CURRENT_PRICE': float("{:.2f}".format(current_stock_price)),
            'PROFIT*1': float("{:.2f}".format(current_stock_price + risk_candle)),
            'PROFIT*2': float("{:.2f}".format(current_stock_price + (risk_candle * 2))),
            'PROFIT*3': float("{:.2f}".format(current_stock_price + (risk_candle * 3)))
        }
    return dict_return


def dumb_risk_analysis_tostring(risk_dict):
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
                + Style.YELLOW + f"@{risk_dict['CURRENT_PRICE']}$"+ Style.END +
                                 f" in the cost of "
                + Style.YELLOW + f"@{risk_dict['TRANSACTION_SIZE']}$ " + Style.END
                + Style.RED + f"\nStop loss @{risk_dict['CURRENT_PRICE']-risk_dict['RISK_CANDLE']}" + Style.END
                + Style.BOLD + f"\nStops:" + Style.END
                + Style.GREEN + f"\n    Sell in @{risk_dict['PROFIT*1']}$ for a {risk_dict['RISK']}$ gain (x2 the risk) " + Style.END
                + Style.GREEN2 + f"\n    Sell in @{risk_dict['PROFIT*2']}$ for a {risk_dict['RISK'] * 2}$ gain (x3 the risk)" + Style.END
                + Style.GREEN + f"\n    Sell in @{risk_dict['PROFIT*3']}$ for a {risk_dict['RISK'] * 3}$ gain (x4 the risk)" + Style.END)
    else:
        return Style.RED + f"Ticker is not valid, but buy: {risk_dict['RISK/RISK_CANDLE']} shares!" + Style.END


print("----------------------")
print(dumb_risk_analysis_tostring(dumb_risk_analysis()))
print("----------------------")
