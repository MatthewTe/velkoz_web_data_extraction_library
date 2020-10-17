# Importing 3rd party packages:
import pandas as pd

"""
The script contains methods that are used to assist in the compilation of stock
data pipelines. The methods within this script perform operations that are not
strictly necessary to make use of the data extraction library, but it simplifies
various processes that need to be done when constructing data pipelines at scale.
These compile methods all pertain to the stock data pipeline libraries. They involve:

* Generating a list of stock ticker symbols from a csv containing ticker symbols.

"""

def compile_ticker_list(csv_file):
    """
    The method reads a .csv file and searches for a column within said csv file
    with the name "ticker_symbols" via the pandas data library ".read_csv" method.
    If this column is found, the method iterates over each row and extracts each
    ticker symbol. Each ticker symbol is then formatted and compiled into a list.
    It is meant to serve as a “helper” method that is used within a scheduler such
    as Airflow to assist in initializing large amounts of stock data
    WebPageResponseObjects.

    Args:
        csv_file (string): The path string to a csv file that the method will
            open.

    Returns:
        list: The list of formatted ticker symbols extracted from the csv file.

    """
    # Opening a csv file as a pandas dataframe:
    ticker_df = pd.read_csv(csv_file)

    # Searching the dataframe for a column with header "ticker_symbols":
    try:
        ticker_symbol_col = ticker_df['ticker_symbols']

    except:

        raise ValueError("No Ticker Symbol Column Found in csv.")

    # Converting the ticker symbol column to a list:
    ticker_symbol_lst = ticker_symbol_col.to_list()

    return ticker_symbol_lst
