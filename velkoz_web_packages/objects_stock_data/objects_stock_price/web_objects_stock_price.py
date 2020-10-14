# Importing native packages:
import time

# Importing thrid party packages:
import requests
from bs4 import BeautifulSoup
import datetime
import yfinance as yf

class NASDAQStockPriceResponseObject(yf.Ticker):
    """
    This is the WebPageResponse Object that is meant to represent the price data
    for publicly listed companies on the NASDAQ from Yahoo Finance.

    This WebPageResponse Object inherits directly from the yfinance.Ticker object
    and makes use of the native methods of the Ticker object to extract data. This
    is a very bare bones WebPageResponse Object as its only purpose is to serve as
    a compatibility wrapper for the yfinance.Ticker object to the StockPriceDataIngestionEngine.
    Critically this is one of the few WebPageResponse Objects that does not inherit
    from the BaseWebPageResponse Object.

    Args:

        ticker (str): The string representing the ticker symbol of the stock that
            the WebResponseObject represents.

    Attributes:

        _ticker (str): The string representing the ticker symbol of the stock that
            the WebResponseObject represents.

        _price_history_full (pandas.dataframe): The pandas dataframe containing
            all of the historical price data of the ticker symbol. The dataframe
            is the result of the yf.Ticker.history(period='max') method. Price
            data is stored in the format:

            +-----------------+-------+-------+-------+-------+--------+-----------+--------------+
            |   date (index)  | open  |  high |  low  | close | volume | dividends | stock_splits |
            +=================+=======+=======+=======+=======+========+===========+==============+
            |    DateTime     | Float | Float | Float | Float |   Int  |   Float   |    Float     |
            +-----------------+-------+-------+-------+-------+--------+-----------+--------------+

            It should be noted that the yf.Ticker.history() method that generates
            the dataframe has its own dataframe column naming scheme. This schema
            is immediately overwritten with a naming convention that is more consistent
            with a database table schema:

                * 'Date'         --> 'date'
                * 'Open'         --> 'open'
                * 'High'         --> 'high'
                * 'Low'          --> 'low'
                * 'Close'        --> 'close'
                * 'Volume'       --> 'volume'
                * 'Dividends'    --> 'dividends'
                * 'Stock Splits' --> 'stock_splits'

        _initialized_time (float): The python timestamp when the object was
            initialized. It is created at the instance the WebObject is initialized
            via datetime.datetime.now()

    References:

        * https://github.com/ranaroussi/yfinance
        * https://stackoverflow.com/questions/576169/understanding-python-super-with-init-methods
    """
    def __init__(self, ticker):

        # Initalizing the yf.Ticker parent object:
        super().__init__(ticker)

        # Declaring instance parameters / re-mapping yf.Ticker params:
        self._ticker = ticker
        self._initialized_time = datetime.datetime.now()

        # Declaring the full price history dataframe and renaming column names for db schema:
        self._price_history_full = self.history(period="max").rename(columns = {
                "Date" : "date",
                "Open" : "open",
                "High" : "high",
                "Low" : "low",
                "Close": "close",
                "Volume": "volume",
                "Dividends" : "dividends",
                "Stock Splits" : "stock_splits"
                })
