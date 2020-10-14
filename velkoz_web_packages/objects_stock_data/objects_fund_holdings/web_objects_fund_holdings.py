# Importing Base Web Objects:
from velkoz_web_packages.objects_base.web_objects_base import BaseWebPageResponse

# Importing 3rd party packages:
import requests
from bs4 import BeautifulSoup
import datetime
import yfinance as yf
import pandas as pd

class NASDAQFundHoldingsResponseObject(BaseWebPageResponse):
    """
    This Web Page Response Object is designed to represent the top 10 holdings of
    a particular Fund listed on the NASDAQ extracted through Yahoo Finance.

    The Object is initialized by a ticker symbol and makes use of the yfinance python
    package to determine if the input ticker is a fund that would contain holdings
    data. If its status is confirmed then the NASDAQFundHoldingsResponseObject’s Parent
    Object is initialized using a custom built Yahoo Finance URL.

    Once the parent object has been initialized, the html stored in the http_response
    is parsed via internal methods to extract the holdings data as a dataframe. This
    dataframe is then represented as an internal parameter.

    Args:

        ticker (str): The string representing the ticker symbol of the stock that
            the WebResponseObject represents.

    Attributes:

        _ticker (str): The string representing the ticker symbol of the stock that
            the WebResponseObject represents.

        _yhfinance_url (str): The url to the Yahoo Finance page that displays
            information about a particular ticker symbol. It is built using the
            input ticker parameter.

        _holdings_tbl (bs4.element.Tag): The BeautifulSoup object representing the html table
            extracted from the Yahoo Finance holdings page. This bs4 object is
            converted to a pandas dataframe via the pd.read_html method.

        _holdings_data (pandas.Dataframe): The dataframe that contains the top
            10 holding of the fund, extracted from the Yahoo Finance page's html
            content via the _extract_holdings_data() method. The dataframe is
            in the format:

            +------------------+--------+-----------------+
            |  symbol (index)  | name   | percent_holdings|
            +==================+========+=================+
            |       string     | string |      float      |
            +------------------+--------+-----------------+

    """
    def __init__(self, ticker):

        self._ticker = ticker

        # Initalizing the yfinance object to test for ticker type:
        yf_ticker_information = yf.Ticker(ticker).info

        # Performing ticker type checking to ensure ticker contains holdings data:
        if yf_ticker_information['quoteType'] == 'EQUITY':
            return

        # Declaring the base url for the holdings page of Yahoo Finance:
        self._yhfinance_url = f"https://finance.yahoo.com/quote/{self._ticker}/holdings"

        # Creating the HTTP request parameter to be passed into GET request:
        ticker_holdings_param = {"p": self._ticker}

        # Initalizing the BaseWebPageResponse parent object with the base url:
        super().__init__(self._yhfinance_url, params = ticker_holdings_param)

        # Extracting holdings dataframe from the HTML response:
        self._holdings_data = self._extract_holdings_data(self._html_body)

    def _extract_holdings_data(self, html_content):
        """
        The internal method parses a body of html content and extracts the data
        table containing the firm’s holdings data as a pandas dataframe.

        The method is intended to parse the html content of the GET request sent
        by the parent method. It converts the html body to a BeautifulSoup object
        in order to make use of its search methods. It parses the soup for the html
        table containing the holdings information. If this information is found, it
        is extracted as a pandas dataframe and returned.


        Args:
            html_content (bytes): The raw html being passed into the method that
                will be parsed for holdings information.

        Returns:
            pandas.Dataframe: The holdings information extracted from the HTML
                content converted to a pandas dataframe.

        References:
            * https://stackoverflow.com/questions/56967976/convert-html-table-to-pandas-data-frame-in-python
        """
        # Converting html body into a BeautifulSoup Object:
        soup = BeautifulSoup(html_content, 'html.parser')

        #print(soup.prettify())

        # Searching for the holdings html table:
        self._holdings_tbl = soup.find('table', attrs={
            "class":"W(100%) M(0) BdB Bdc($seperatorColor)"})

        # Attempting to create a pandas dataframe from the html table:
        holdings_df = pd.read_html(str(self._holdings_tbl))[0]

        # Formatting dataframe to appropriate schema:
        holdings_df.rename(columns = {
            "Name":"name", "Symbol":"symbol", "% Assets": "percent_holdings"},
            inplace=True)

        # Converting percentage strings to float (drop "%" then str -> float):
        holdings_df['percent_holdings'] = holdings_df['percent_holdings'].map(
            lambda x : float(x.replace("%", "")))

        holdings_df.set_index('symbol', inplace=True)

        return holdings_df
