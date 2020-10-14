# Importing testing frameworks:
import unittest

# Importing 3rd party packages for testing:
import pandas as pd
import bs4
import numpy as np

# Importing velkoz web packages for testing:
from velkoz_web_packages.objects_stock_data.objects_fund_holdings.web_objects_fund_holdings import NASDAQFundHoldingsResponseObject

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
        # Creating a FundHoldings Objects for various funds:
        icln_holdings = NASDAQFundHoldingsResponseObject("ICLN")
        qcln_holdings = NASDAQFundHoldingsResponseObject("QCLN")
        voo_holdings = NASDAQFundHoldingsResponseObject("VOO")

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
