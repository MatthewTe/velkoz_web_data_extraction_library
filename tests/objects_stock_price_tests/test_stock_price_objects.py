# Importing testing frameworks:
import unittest

# Importing 3rd party packages:
import bs4
import sqlite3
import sqlalchemy
import pandas as pd
import numpy as np
import datetime

# Importing velkoz web packages for testing:
from velkoz_data_pipeline.velkoz_web_packages.objects_stock_price.web_objects_stock_price import NASDAQStockPriceResponseObject


class NASDAQStockPriceResponseObjectTest(unittest.TestCase):

    def test_stock_price_object_parent(self):
        """
        The method tests the initalization of the NASDAQStockPriceResponseObject's
        parent object yf.Ticker.

        The method initalizes a NASDAQStockPriceResponseObject for the ticker
        'AAPL' and type checks all of the internal parameters for the WebResponseObject.
        The method also tests the pandas dataframe column names and datatypes
        as well as the index data type of the '_price_history_full' parameter
        to ensure price timeseries data is being extracted correctly as well as
        other interal parameters that are defined within the StockPriceResponse
        Object such as the 'initialized_time'.

        """
        # Initalizing the StockPrice Response Object:
        appl = NASDAQStockPriceResponseObject("AAPL")

        # Type Checking the '_price_history_full' dataframe:
        self.assertIsInstance(appl._price_history_full, pd.DataFrame)

        # Declaring the appropriate list of column names for the '_price_history_full' df:
        column_names_lst = sorted(['open', 'high', 'low', 'close', 'volume', 'dividends', 'stock_splits'])

        # Testing the column names of the price_history dataframe:
        self.assertEqual(column_names_lst, sorted(appl._price_history_full.columns))

        # Type testing the data from each column in the '_price_history_full':
        self.assertIs(appl._price_history_full.open.dtype, np.dtype('float64'))
        self.assertIs(appl._price_history_full.high.dtype, np.dtype('float64'))
        self.assertIs(appl._price_history_full.low.dtype, np.dtype('float64'))
        self.assertIs(appl._price_history_full.close.dtype, np.dtype('float64'))
        self.assertIs(appl._price_history_full.volume.dtype, np.dtype('int64'))
        self.assertIs(appl._price_history_full.dividends.dtype, np.dtype('float64'))
        self.assertIs(appl._price_history_full.stock_splits.dtype, np.dtype('float64'))

        # Type Testing the Data in the price_history dataframe index:
        self.assertIsInstance(appl._price_history_full.index, pd.DatetimeIndex)

        # Type testing the '_initialized_time' internal parameter:
        self.assertIsInstance(appl._initialized_time, datetime.datetime)
