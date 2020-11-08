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

# Interating through ticker lists creating Response Objects:
stock_response_obj_lst = [NASDAQStockPriceResponseObject(ticker) for ticker in stock_ticker_lst]
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
        self.assertIsInstance(ingestion_engine._sqlaengine, sqlalchemy.engine.Engine)
        self.assertIsInstance(ingestion_engine._db_session_maker, sqlalchemy.orm.session.sessionmaker)
        self.assertIsInstance(ingestion_engine._db_session, sqlalchemy.orm.scoped_session)
        
