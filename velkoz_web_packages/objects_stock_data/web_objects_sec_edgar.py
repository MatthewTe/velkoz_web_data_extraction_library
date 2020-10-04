# Importing 3-rd party modules:
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Importing base web objects:
from base_objects import BaseWebPageResponse, BaseWebPageIngestionEngine

class EDGARResultsPageResponse(BaseWebPageResponse):
    """
    This is a class that inherits from the BaseWebPageResponse object and represents
    the results of the SEC's EDGAR response page.

    It contains all of the internal methods for extracting relevant data from
    the EDGAR Search Results page of a specific ticker url. The url used to
    initialize the object can be input directly or built using an external
    CIK# to url API. The Attributes listed below are the additional attributes
    that are added to the Base class BaseWebPageResponse.

    Attributes:
        _addr_business (str): A string representing the Business Address of the
            company extracted from the BeautifulSoup object via the
            __extract_address() method.

        _addr_mail (str): A string representing the Mailing Address of the
            company extracted from the BeautifulSoup object via the
            __extract_address() method.

        _reports_tbl (pandas dataframe): A dataframe containing all the contents
            that were extracted from the main search results table on the EDGAR
            company reports page. The dataframe contains the following columns:

            ---------------------------------------------------------------------------------------------------------
            |filing|filing_description|filing_date|file_id|report_contents_html|report_contents_txt|report_data_href|
            |------------------------------------------------------------------|-------------------|----------------|
            |  str |        str       |     str   |  str  |BeautifulSoup Object|         str       |       str      |
            ---------------------------------------------------------------------------------------------------------

    """

    def __init__(self, url, **kwargs):

        # Re-deffiing url and kwargs to facilitate pass through to parent object:
        self.kwargs = kwargs
        self._url = url

        # Initalizing the base method:
        super().__init__(url, **kwargs)

        # Declaring instance variables specific to EDGAR HTML page:

        # Company Header Information:
        self._addr_mail = self.__extract_address()['mailing'] or 'NaN'
        self._addr_business = self.__extract_address()['business'] or 'NaN'

        # Company Filing Table Information:
        self._reports_tbl = self.__extract_company_report_data() # Pandas dataframe

    def __extract_address(self):
        '''
        The internal method that parses the main BeautifulSoup object for the
        <div> tags containing the strings of the company's address information.
        The EDGAR result page contains two addresses (Business and Mailing Address).
        This method extracts both Business and Mailing address div tags. It
        concats each of these addresses into a len(2) dictionary as:
        {'mailin_address': mailing_address, 'business_address':business_address}.

        Returns:
            dict: The two length dict containing both the business and mailing address.

        '''

        # Searching the main soup for the tag <div class='mailer'>:
        mailer_div_tags = self._html_body.find_all('div', class_='mailer')

        # Iterating through each of the <div class='mailer'> and concating string
        # via list comprehension: [Mailing Address, Business Address]
        concat_addr_str = [
            ' '.join(mailer_div_tag.text.split()) for mailer_div_tag in mailer_div_tags]

        # Returning the dict {'mailing', 'business'}:
        return {
            # Formatting address string to remove 'title markers':
            'mailing': concat_addr_str[0].replace('Mailing Address', ''),
            'business': concat_addr_str[1].replace('Business Address', '')}

    def __extract_company_report_data(self):
        '''
        Method extracts and pre-processes all the data associated with the
        table of reports filed by the company on the EDGAR web page.

        In addition to extracting the textual data from basic rows: 'Filings',
        'Filing Date' etc the method also navigates to the pages containing the
        associated full document in HTML format as well as the summary information
        provided in the 'Interactive Data' page stored in .csv format. Both the
        document and the .csv are stored within a pandas dataframe alongside the
        basic textual data.

        Returns:
            pandas dataframe: The dataframe containing all relevant information
                extracted from the table of reports filed on the EDGAR results page.

        '''

        # Extracting the table from the main webpage soup:
        html_table = self._html_body.find('table', class_='tableFile2')

        # Extracting a list of table row objects <tr> from the table:
        tbl_row_lst = html_table.find_all('tr')

        # First <tr> in tbl_row_lst are headers. Using headers to authenticate
        # rest of table:
        tbl_headers = [
            # Creating a list of the text of each table row:
            tbl_row.text for tbl_row in tbl_row_lst.pop(0).find_all('th')]

        # Manually comparing the tbl_headers for table validation:
        if tbl_headers == ['Filings', 'Format', 'Description', 'Filing Date', 'File/Film Number']:

            # TODO: If Logging- Log the headers validation passed.

            # Creating list of be populated by each row:
            row_lst = []

            # Building a list of lists for each row in the table [[row_1],... [row_n]]
            # where each row = [cell_1, cell_2, cell_3, cell_4, str(cell_4), cell_5]:
            for table_row in tbl_row_lst:

                # Extracing all cells for each row:
                table_cells = table_row.find_all('td')

                # Formatting 'Description' Cell:
                description = " ".join(table_cells[2].text.split())

                # Formatting Filing Data cell:
                filing_date = table_cells[3].text

                # Formatting File Number:
                file_num = table_cells[4].text or 'NaN'

                # Extracting the data from the 'Format' cell:
                format_doc = self.__extract_report_html(
                    table_cells[1].find('a', id='documentsbutton')['href']) or 'NaN'

                # Attempting to extract only text from format_doc bs4 object:
                format_doc_txt = format_doc.get_text('/n') or 'NaN'

                # try-catch to get around ['href'] breaking 'or NaN' convention:
                try:
                    format_data_interactive = self.__extract_report_csv(
                        table_cells[1].find('a', id='interactiveDataBtn')['href'])

                except:
                    format_data_interactive = 'NaN'

                # Creating internal list of cells from table_cells list of len(5):
                row = [
                    table_cells[0].text, # 'Filings' cell needs no Formatting
                    description, # The description of the Report
                    filing_date, # The date the report was filed
                    file_num, # The SEC internal file number for the report
                    format_doc, # The full HTML contents of the report.
                    format_doc_txt, # The textual content of the report.
                    format_data_interactive # The link to the tabular data of the report
                    ]

                # Adding row to the list of rows:
                row_lst.append(row)

            # Converting the list of rows into a pandas dataframe:
            report_df = pd.DataFrame(row_lst, columns=[
                'filing', 'filing_description', 'filing_date', 'file_id',
                'report_contents_html', 'report_contents_txt', 'report_data_href'])

            return report_df


        else:
            raise AssertionError('Table Headers Do Not Match- EDGAR Reports  table format may have changed')

    def __extract_report_html(self, report_href):
        '''
        A method that takes the href to the full report document extracted by the
        __extract_company_report_data() method and extracts the full HTML file of
        the report.

        The href parameter routes to the Document Format Files page. The method
        navigates to the href on said page that leads to the report, displayed in
        the SEC's Inline XBRL Viewer. It manipulates the href into a direct link
        to the html version of the report. This html page is extracted and returned
        as a bs4 object.

        Args:
            report_href (str): The href extracted from a previous bs4 object in
                string format. This method operates under the assumption that the
                href is extracted from the main EDGAR results page and leads to
                the SEC's Inline XBRL Viewer.

        Returns:
            BeautifulSoup obj: A bs4 object containing all the html contents of the
                report.
        '''

        # Appending href onto core url to make funcional url:
        doc_selector_url = 'https://www.sec.gov' + report_href

        # Sending GET request to new webpage and converting contents to bs4 object:
        docs_page = BeautifulSoup(requests.get(doc_selector_url).content, 'html.parser')

        # Extracting the <table summary = 'Document Format Files'> from the page:
        doc_format_table = docs_page.find('table', summary='Document Format Files')

        # Extracting the .htm href from the Document format table. Row=2, Col=3:
        table_rows = doc_format_table.find_all('tr')

        # Converting table header to list of strings for validation:
        table_header = [header.text for header in table_rows[0].find_all('th')]

        # Using the headers of the tables: table_rows[0] for validation:
        if table_header == ['Seq', 'Description', 'Document', 'Type', 'Size']:

            # Extracting the href from the second cell of Row 2 of the table:
            document_url = 'https://www.sec.gov' + table_rows[1].find('a')['href']

            # Dropping the '/ix?doc=' from the href if it is there so that only HTML
            # content is returned:
            if '/ix?doc=' in document_url:
                document_url = document_url.replace('/ix?doc=', '')

            # Performing a GET request for the full report in HTML:
            report_response = requests.get(document_url)

            # returning the bs4 object of the HTTP response's content:
            return BeautifulSoup(report_response.content, 'html.parser')

        else:
            raise AssertionError('The Table Header for Document Format Files Failed. The Layout May have changed')

    def __extract_report_csv(self, report_csv_href):
        '''
        A method that extracts a .csv of all summary data from the report href.

        The method takes the an href to the report's 'Interactive Data' page. It
        extracts the href to the .xlsx file containing the tabular data from the
        main report (previously extracted via the __extract_report_html() method).
        It returns the full url for the .xlsx file.

        Args:
            report_csv_href (str): The href to the 'Filings Data' page. It is
                assumed that hrefs passed into this method are extracted from the
                main company reports page's 'Interactive Data' button.

        Returns:
            str: The full url of the .xlsx file.

        '''

        # Building a full url to the 'filing Data' page:
        filing_data_url = 'https://www.sec.gov' + report_csv_href

        # Sending GET request to the page and converting contents to bs4 object:
        filing_data_page = BeautifulSoup(requests.get(filing_data_url).content,
            'html.parser')

        # Parsing the filing data page for the .xlsx download href:
        # Assumes only two <a class='xbrlviewer'> on page:
        xlsx_href =  filing_data_page.find_all('a', class_='xbrlviewer')[1]['href']

        # Creating and returning the download url for the .xlsx file:
        return 'https://www.sec.gov' + xlsx_href



# Test:
# test = EDGARResultsPageResponse('https://www.sec.gov/cgi-bin/browse-edgar', params={'CIK':'0000320193'})
