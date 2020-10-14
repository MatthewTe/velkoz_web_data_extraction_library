# Importing 3-rd party modules:
import requests
from bs4 import BeautifulSoup
import pandas as pd


class EDGARPageIngestionEngine(BaseWebPageIngestionEngine):
    """
    The EDGARPageIngestionEngine object is the object used to connect the raw
    data extracted via instances of the EDGARResultsPageResponse() object to a database.

    The ingestion engine performs data transformation on the parameters of an
    EDGARResultsPageResponse() object and writes said formatted data to a backed database
    via the SQLAlchemy ORM. When this object is initialized its instance variables
    contain metadata on the database tables that it has accessed/created. The
    actual writing to the database is done by calling an internal writing method.
    # TODO: Once Method is written describe it.

    The ingestion engine is designed to ingest multiple instances of the EDGARResultsPageResponse()
    object through the *args parameter and as such the method that performs the data
    ingestion iterates through the list of *argments and performs the specific
    writing operation for each instance of EDGARResultsPageResponse().

    Attributes:
        # TODO: Add attributes

    """
    pass
