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
from velkoz_web_packages.objects_stock_data.web_objects_stock_price import NASDAQStockPriceResponseObject
from velkoz_web_packages.objects_stock_data.ingestion_engines_stock_price import StockPriceDataIngestionEngine
from velkoz_web_packages.objects_base.ingestion_engines_base import BaseWebPageIngestionEngine

# Declaring several StockPrice Objects for Ingestion Engine Test:
aapl = NASDAQStockPriceResponseObject('AAPL')
tsla = NASDAQStockPriceResponseObject('TSLA')
xom = NASDAQStockPriceResponseObject("XOM")
nee = NASDAQStockPriceResponseObject('NEE')

# Declaring BaseWebPageResponse Objects for Validation testing for Ingestion Engine:
google = BaseWebPageResponse('https://www.google.com/')
stack_overflow = BaseWebPageResponse('https://stackoverflow.com/')

# Creating lists of StockPrice Objects to test sequential data ingestion:
ticker_lst = [tsla, xom, nee]
mixed_web_obj_lst = [google, xom, tsla, stack_overflow]

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


class StockPriceDataIngestionEngineTest(unittest.TestCase):

    def test_stock_price_ingestion_engine_functionality(self):
        """
        The method performs integration tests on the StockPriceDataIngestionEngine
        which is designed to ingest WebPageResponseObjects that contain time-series
        price data and write them to a database using the appropriate schema.

        The method tests all of the parent and extended functionality of the Ingestion
        Engine methods that do not involve writing data to a database. The functionality
        that is being tested includes:

        * The ability to successfully manipulate the WebResponseObjects list (add, remove, purge).
        * The ability of the internal validation methods to successfully validate
            ingested objects (only validating supported WebResponseObject types).
        * The successful creation of a database connection, database engine and
            associated scoped  database session.

        """
        # Initalzing a StockPriceDataIngestionEngine Instance:
        ingestion_engine = StockPriceDataIngestionEngine(
            "sqlite:///:memory:", aapl)

        # Performing type checking on all internal SQLAlchemy database conn objects:
        self.assertIsInstance(ingestion_engine._sqlaengine, sqlalchemy.engine.Engine)
        self.assertIsInstance(ingestion_engine._db_session_maker, sqlalchemy.orm.session.sessionmaker)
        self.assertIsInstance(ingestion_engine._db_session, sqlalchemy.orm.scoped_session)

        # Asserting the length of the internal WebObject list (should be 1):
        self.assertEqual(len(ingestion_engine._WebPageResponseObjs), 1)

        # Iterating over a list of WebObjects, performing individual ingestion:
        for web_object in ticker_lst:
            ingestion_engine._insert_web_obj(web_object)

        # Asserting the length of the internal WebObject list (should be 4):
        self.assertEqual(len(ingestion_engine._WebPageResponseObjs), 4)

        # Purging the list of all elements:
        ingestion_engine._purge_web_obj_que()

        # Asserting the length of the internal WebObject list (should be 0):
        self.assertEqual(len(ingestion_engine._WebPageResponseObjs), 0)

        # Ingesting a mixed list of WebObjects to test validation status:
        for web_obj in mixed_web_obj_lst:
            ingestion_engine._insert_web_obj(web_obj)

        # Asserting the length of the internal WebObject list (should be 4):
        self.assertEqual(len(ingestion_engine._WebPageResponseObjs), 4)

        # Performing the main data type validation method externally for testing:
        validation_dict = ingestion_engine._validate_args()

        # Asserting that the Ingestion Engine has accurately validated the Web Objects:

        # Objects that should have been validated as compatable with the Ingestion Engine:
        self.assertEqual(validation_dict[xom], 20)
        self.assertEqual(validation_dict[tsla], 20)

        # Objects that should have been validated as incompatable with the Ingestion Engine:
        self.assertEqual(validation_dict[google], 10)
        self.assertEqual(validation_dict[stack_overflow], 10)
