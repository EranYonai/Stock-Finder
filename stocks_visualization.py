# Raw packages
import numpy as np
import pandas as pd
# Data Source
import yfinance as yf
# Data visualization
import plotly.graph_objs as go


def download(ticker, dates, interval):
    return yf.download(tickers=ticker, period=dates, interval=interval)


def show_graph(data):
    fig = go.Figure()  # Decalre on figure
    fig.add_trace(go.Candlestick(x=data.index,
                                 open=data['Open'],
                                 high=data['High'],
                                 low=data['Low'],
                                 close=data['Close'], name='market data'))
    fig.update_layout(title='A title', yaxis_title='Stock Price $', yaxis_range=[525, 535])
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

data = download('NFLX', '1d', '2m')
show_graph(data)
