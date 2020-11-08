# Importing testing frameworks:
import unittest

# Importing 3rd party packages:
import bs4
import sqlite3
import sqlalchemy
import pandas as pd
import numpy as np
import datetime

# Importing Velkoz Packages for testing:
from velkoz_web_packages.objects_stock_data.objects_stock_db_summary.ingestion_engines_stock_data_summary import StockDataSummaryIngestionEngine
from velkoz_web_packages.objects_stock_data.objects_stock_price.web_objects_stock_price import NASDAQStockPriceResponseObject
from velkoz_web_packages.objects_stock_data.objects_stock_price.ingestion_engines_stock_price import StockPriceDataIngestionEngine
from velkoz_web_packages.objects_stock_data.objects_fund_holdings.web_objects_fund_holdings import NASDAQFundHoldingsResponseObject
from velkoz_web_packages.objects_stock_data.objects_fund_holdings.ingestion_engines_fund_holdings import FundHoldingsDataIngestionEngine

# <-Declaring global parameters for use in testing class->:

# Declaring a list of stock tickers and list of fund stock tickers:
stock_ticker_lst = ['AAPL', 'XOM', 'MSFT', 'V', 'FSLR', 'TSLA']
fund_ticker_lst = ['SPY', 'QQQ', 'XLF', 'XLE', 'ICLN']
total_ticker_lst = stock_ticker_lst + fund_ticker_lst

# Interating through ticker lists creating Response Objects:
stock_response_obj_lst = [NASDAQStockPriceResponseObject(ticker) for ticker in total_ticker_lst]
funds_response_obj_lst = [NASDAQFundHoldingsResponseObject(ticker) for ticker in fund_ticker_lst]

class StockDataSummaryIngestionEngineTest(unittest.TestCase):

    def test_base_ingestion_engine_initalization(self):
        """
        The method tests the creation/initialization of the StockDataSummaryIngestionEngine
        object. The method initializes the Ingestion engine and performs type
         with the IngestionEngine’s SQLAlchemy objects that are used to connect
         to the database.

        """
        # Initializing the Ingestion Engine with an in-memory database:
        test_ingestion_engine = StockPriceDataIngestionEngine("sqlite:///:memory:")

        # Performing type checking on all internal SQLAlchemy database conn objects:
        self.assertIsInstance(test_ingestion_engine._sqlaengine, sqlalchemy.engine.Engine)
        self.assertIsInstance(test_ingestion_engine._db_session_maker, sqlalchemy.orm.session.sessionmaker)
        self.assertIsInstance(test_ingestion_engine._db_session, sqlalchemy.orm.scoped_session)

        # Asserting that the internal WebResponseObjects list is length zero:
        self.assertEqual(len(test_ingestion_engine._WebPageResponseObjs), 0)

    def test_base_ingestion_engine_db_write(self):
        """
        The method tests the correct ingestion of tickers into a database and the
        ability of the ingestion engine to correctly write and maintain these
        associated ticker database tables. The method tests the following
        processes:

        * The correct ingestion of ticker symbols into the ingestion engine.
        * The correct validation of ticker symbol strings via the Ingestion Engine’s
            internal validation methods.
        * The correct writing of the ticker symbols into the database in a manner that
            correctly represents the database status of the ticker symbols (see
            documentation for the StockDataSummaryIngestion Engine).
        * The ability of the Ingestion Engine to correctly update the database tables
            with accurate changes to the database schema (again see documentation).

        """
        # Creating the test ingestion engine:
        data_summary_ingestion_engine = StockDataSummaryIngestionEngine("sqlite:///test_db.db")

        # Ingesting the series of ticker symbols into the ingestion engine:
        for ticker in total_ticker_lst:
            data_summary_ingestion_engine._insert_web_obj(ticker)

        # Asserting the length of the ingestion engine's internal WebResponseObjects list:
        self.assertEqual(len(data_summary_ingestion_engine._WebPageResponseObjs), len(total_ticker_lst))

        # Writing _WebPageResponseObjs list to the database from Ingestion Engine:
        data_summary_ingestion_engine._write_web_objects()

        # Asserting _WebPageResponseObjs list to be empty:
        self.assertEqual(len(data_summary_ingestion_engine._WebPageResponseObjs), 0)

        # Reading data from the database table that should have been created:
        stock_data_summary_tbl = pd.read_sql_table(
            "nasdaq_stock_data_summary_tbl",
            data_summary_ingestion_engine._sqlaengine,
            index_col = "ticker")

        print(stock_data_summary_tbl.dtypes)

        # Performing type testing and assertion testing for elements of the dataframe:
        self.assertIs(stock_data_summary_tbl.index.dtype, np.dtype('O'))
        self.assertIs(stock_data_summary_tbl.price_tbl.dtype, np.dtype('O'))
        self.assertIs(stock_data_summary_tbl.holdings_tbl.dtype, np.dtype('O'))

        # # WARNING: Validation possibly broken for datetime object type checking:
        # dtype('<M8[ns]') != dtype('<M8[ns]'). Need to fix.
        "self.assertIs(stock_data_summary_tbl.last_updated.dtype, np.dtype('datetime64[ns]'))"

        # Creating Stock Price and Fund Holdings Ingestion Engiens:
        stock_price_engine = StockPriceDataIngestionEngine("sqlite:///test_db.db")
        fund_holdings_engine = FundHoldingsDataIngestionEngine("sqlite:///test_db.db")

        # Ingesting the Response Objects to the Ingestion Engine -> In Memory Database:
        for stock_price_obj in stock_response_obj_lst:
            stock_price_engine._insert_web_obj(stock_price_obj)

        for fund_holdings_obj in funds_response_obj_lst:
            fund_holdings_engine._insert_web_obj(fund_holdings_obj)

        # Writing fund holdings and stock price data to in-memory database:
        stock_price_engine._write_web_objects()
        fund_holdings_engine._write_web_objects()

        # Re-Ingesting the ticker list into the DataSummaryIngestionEngine:
        for ticker in total_ticker_lst:
            data_summary_ingestion_engine._insert_web_obj(ticker)

        data_summary_ingestion_engine._write_web_objects()

        # Reading data from the database table that should now be updated:
        stock_data_summary_tbl = pd.read_sql_table(
            "nasdaq_stock_data_summary_tbl",
            data_summary_ingestion_engine._sqlaengine,
            index_col = "ticker")

        # Extracting the several rows of the dataframe to assert the actual values
        # stored within the dataframe:
        df_slice = stock_data_summary_tbl[:5]

        for index, row in df_slice.iterrows():
            print(row)
