# Importing testing frameworks:
import unittest

# Importing 3rd party packages for testing:
import sqlite3
import sqlalchemy
import pandas as pd
import bs4
import numpy as np

# Importing velkoz web packages for testing:
from velkoz_web_packages.objects_stock_data.objects_fund_holdings.web_objects_fund_holdings import NASDAQFundHoldingsResponseObject
from velkoz_web_packages.objects_stock_data.objects_fund_holdings.ingestion_engines_fund_holdings import FundHoldingsDataIngestionEngine
from velkoz_web_packages.objects_stock_data.objects_stock_price.web_objects_stock_price import NASDAQStockPriceResponseObject

# Creating NASDAQFundHoldingsResponseObjects for testing:
icln_holdings = NASDAQFundHoldingsResponseObject("ICLN")
qcln_holdings = NASDAQFundHoldingsResponseObject("QCLN")
voo_holdings = NASDAQFundHoldingsResponseObject("VOO")
aapl_price_obj = NASDAQStockPriceResponseObject('AAPL')
tsla_price_obj = NASDAQStockPriceResponseObject('TSLA')

mixed_web_obj_lst = [icln_holdings, qcln_holdings, voo_holdings, aapl_price_obj, tsla_price_obj]

class NASDAQFundHoldingsResponseObjectTest(unittest.TestCase):

    def test_fund_holding_web_object_data_extraction(self):
        """
        This method tests the NASDAQFundHoldingsResponseObject’s ability to extract
        the correct data from Yahoo Finance.

        It performs assertion tests that test the object's ability to:

        * Accurately construct a Yahoo Finance holdings GET request based on an input ticker
        * Correctly parse the HTML response to said GET request for “Top 10 Holdings Table”.
        * Converts the extracted html table to a pandas DataFrame that is correctly formatted and typed.

        """
        # Testing the accuracy of the url generator:
        self.assertEqual("https://finance.yahoo.com/quote/ICLN/holdings", icln_holdings._yhfinance_url)
        self.assertEqual("https://finance.yahoo.com/quote/ICLN/holdings?p=ICLN", icln_holdings._http_response.url)

        self.assertEqual("https://finance.yahoo.com/quote/QCLN/holdings", qcln_holdings._yhfinance_url)
        self.assertEqual("https://finance.yahoo.com/quote/QCLN/holdings?p=QCLN", qcln_holdings._http_response.url)

        self.assertEqual("https://finance.yahoo.com/quote/VOO/holdings", voo_holdings._yhfinance_url)
        self.assertEqual("https://finance.yahoo.com/quote/VOO/holdings?p=VOO", voo_holdings._http_response.url)

        # Type Checking the holdings_tbl BeautifulSoup object:
        self.assertIsInstance(icln_holdings._holdings_tbl, bs4.element.Tag)
        self.assertIsInstance(qcln_holdings._holdings_tbl, bs4.element.Tag)
        self.assertIsInstance(voo_holdings._holdings_tbl, bs4.element.Tag)

        # Validating the dataframe extracted from the html table of the NASDAQFundHoldingsResponseObject:
        df_column_format = sorted(['name', 'percent_holdings'])
        icln_df_columns = sorted(icln_holdings._holdings_data.columns)
        qcln_df_columns = sorted(qcln_holdings._holdings_data.columns)
        voo_df_columns = sorted(voo_holdings._holdings_data.columns)

        self.assertEqual(icln_df_columns, df_column_format)
        self.assertEqual(qcln_df_columns, df_column_format)
        self.assertEqual(voo_df_columns, df_column_format)

        # Type-checking the dataframe columns:
        self.assertIs(icln_holdings._holdings_data.name.dtype, np.dtype("object"))
        self.assertIs(icln_holdings._holdings_data.percent_holdings.dtype, np.dtype("float64"))
        self.assertIs(icln_holdings._holdings_data.index.dtype, np.dtype('object'))

        self.assertIs(qcln_holdings._holdings_data.name.dtype, np.dtype("object"))
        self.assertIs(qcln_holdings._holdings_data.percent_holdings.dtype, np.dtype("float64"))
        self.assertIs(qcln_holdings._holdings_data.index.dtype, np.dtype('object'))

        self.assertIs(voo_holdings._holdings_data.name.dtype, np.dtype("object"))
        self.assertIs(voo_holdings._holdings_data.percent_holdings.dtype, np.dtype("float64"))
        self.assertIs(voo_holdings._holdings_data.index.dtype, np.dtype('object'))

class FundHoldingsDataIngestionEngineTest(unittest.TestCase):

    def test_fund_holding_data_ingestion(self):
        """
        This method tests the functionality of the FundHoldingsDataIngestionEngine.

        It tests the ability of the Ingestion Engine to successfully validate Ingested
        Web Objects and manage its Que of WebPageResponseObjects. As a result
        this method tests the following functionality of the Ingestion Engine:

        * The ability to successfully manipulate the WebResponseObjects list (add, remove, purge).
        * The ability of the internal validation methods to successfully validate
            ingested objects (only validating supported WebResponseObject types).
        * The successful creation of a database connection, database engine and
            associated scoped  database session.

        """
        # Creating Ingestion Engine Instance connected to an in-memory database:
        ingestion_engine = FundHoldingsDataIngestionEngine(
            "sqlite:///:memory:")

        # Testing the connectivity of the ingestion engine to the database:
        self.assertIsInstance(ingestion_engine._sqlaengine, sqlalchemy.engine.Engine)
        self.assertIsInstance(ingestion_engine._db_session_maker, sqlalchemy.orm.session.sessionmaker)
        self.assertIsInstance(ingestion_engine._db_session, sqlalchemy.orm.scoped_session)

        # Performing assertion testing on the ability of the Ingestion Engine to manage its que of objects:
        self.assertEqual(len(ingestion_engine._WebPageResponseObjs), 0) # Que should be empty currently

        # Adding WebPageResponse Objects into the Ingestion Engine:
        ingestion_engine._insert_web_obj(icln_holdings)
        self.assertEqual(len(ingestion_engine._WebPageResponseObjs), 1) # Que should be len 1

        ingestion_engine._insert_web_obj(qcln_holdings)
        self.assertEqual(len(ingestion_engine._WebPageResponseObjs), 2) # Que should be len 2

        ingestion_engine._insert_web_obj(voo_holdings)
        self.assertEqual(len(ingestion_engine._WebPageResponseObjs), 3) # Que should be len 3

        # Purging the list of all elements:
        ingestion_engine._purge_web_obj_que()

        # Asserting the length of the internal WebObject list (should be 0):
        self.assertEqual(len(ingestion_engine._WebPageResponseObjs), 0)

        # Ingesting a mixed list of WebObjects to test validation status:
        for web_obj in mixed_web_obj_lst:
            ingestion_engine._insert_web_obj(web_obj)

        # Asserting the length of the internal WebObject list (should be 5):
        self.assertEqual(len(ingestion_engine._WebPageResponseObjs), 5)

        # Performing the main data type validation method externally for testing:
        validation_dict = ingestion_engine._validate_args()

        # Asserting that the ingestion engine accurately validated the web_objects:

        # Objects that should have been validated as compatable with the Ingestion Engine:
        self.assertEqual(validation_dict[icln_holdings], 20)
        self.assertEqual(validation_dict[qcln_holdings], 20)
        self.assertEqual(validation_dict[voo_holdings], 20)

        # Objects that should have been validated as incompatable with the Ingestion Engine:
        self.assertEqual(validation_dict[aapl_price_obj], 10)
        self.assertEqual(validation_dict[tsla_price_obj], 10)

    def test_fund_holdings_ingestion_engine_database_update(self):
        """
        This method performs the unit tests for the __add_session_web_obj method.

        This method that is designed to create and update database tables containing
        the data on a funds holdings extracted from a FundHoldingsResponseObject.

        The method tests the Ingestion Engine’s ability to:

        * Create a new table for a ticker if it does not already exist and populate
            it with the most recent pricing data.

        """
        # Creating a populated ingestion engine for testing:
        ingestion_engine = FundHoldingsDataIngestionEngine("sqlite:///:memory:",
            icln_holdings, qcln_holdings,
            voo_holdings)

        # Performing Write Operations:
        ingestion_engine._write_web_objects()

        # Asserting that the correct data was written to the database:
        extracted_db_tbls_lst = sorted(ingestion_engine._sqlaengine.table_names())
        test_db_tbls_lst = sorted(["ICLN_holdings_data", "QCLN_holdings_data", "VOO_holdings_data"])

        self.assertEqual(extracted_db_tbls_lst, test_db_tbls_lst)

        # Extracting data from the in-memory database as pandas dataframe for type-checking:
        icln_data = pd.read_sql_table("ICLN_holdings_data", con=ingestion_engine._sqlaengine, index_col='symbol')
        qcln_data = pd.read_sql_table("QCLN_holdings_data", con=ingestion_engine._sqlaengine, index_col='symbol')
        voo_data = pd.read_sql_table("VOO_holdings_data", con=ingestion_engine._sqlaengine, index_col='symbol')

        # Comparing the read data to the written data to ensure accurate writing:
        self.assertEqual(icln_data.equals(icln_holdings._holdings_data), True)
        self.assertEqual(qcln_data.equals(qcln_holdings._holdings_data), True)
        self.assertEqual(voo_data.equals(voo_holdings._holdings_data), True)
