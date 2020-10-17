# Importing testing frameworks:
import unittest

# Importing library packages for testing:
from velkoz_web_packages.objects_stock_data.stock_data_compiler import compile_ticker_list

class TickerListCompilerTest(unittest.TestCase):

    def test_compile_ticker_list_method(self):
        """
        Method tests the ability of the “compile_ticker_list” method to extract
        a formatted ticker list from a .csv file of ticker symbols. It is a unit
        test of the method that just tests equivalence.
        """
        # Initializing list compiling methods with relative paths to test static files:
        compiled_ticker_lst = compile_ticker_list(
            "tests/static_test_files/static_files_stock_data_test/ticker_list_test_file.csv"
            )

        # Manually declaring ticker list for assertion testing:
        manually_compiled_ticker_lst = [
            "AAPL", "MSFT", "AMZN", "FB", "GOOGL", "BRK.B", "JNJ", "V", "PG",
            "TSLA", "ENPH", "ON", "SEDG", "XOM"
            ]

        # Asserting that the ticker list was compiled correctly:
        self.assertEqual(sorted(compiled_ticker_lst), sorted(manually_compiled_ticker_lst))
