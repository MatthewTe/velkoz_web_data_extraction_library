# Importing Base Ingestion Engine:
from velkoz_web_packages.objects_base.ingestion_engines_base import BaseWebPageIngestionEngine
from velkoz_web_packages.objects_stock_data.objects_fund_holdings.web_objects_fund_holdings import NASDAQFundHoldingsResponseObject

# Importing 3rd party packages:
import requests
from bs4 import BeautifulSoup
import datetime
import yfinance as yf
import pandas as pd


class FundHoldingsDataIngestionEngine(BaseWebPageIngestionEngine):
    """
    This is the Data Ingestion Engine that is used to write WebPageResponse Objects
    relating to a fund's top 10 holdings to a database.

    The IngestionEngine extends/overwrites the BaseWebPageIngestionEngine and is
    designed to be compatible with WebPageResponse Objects that extract fund holdings
    data in the format of FundHoldingsResponse Objects like the  NASDAQFundHoldingsResponseObject.
    It performs data validation for Response Objects that are passed into it to
    ensure this compatibility.

    The Ingestion Engine off-loads the database writing functionality to the pandas
    library due to the simplicity of the data being written. The FundHoldingsResponse
    Objects contain information about the top 10 holdings of a fund, represented as a
    pandas dataframe. This dataframe can easily be read into the relevant database via
    the pandas dataframe.to_sql method. As such it allows the database writing logic to
    be outsourced to pandas for simplicity.

    This simplicity comes at a cost. Notably due to the limitation of the .to_sql
    method, anytime the holdings data for a fund is written to a database that already
    contains previous holdings data the Ingestion Engine does not update the table,
    it drops and replaces it with the new data table. For smaller, simplistic datasets
    such as fund holdings dataframes (and stock price time series), this method of
    updating while inefficient is effective. It may run into performance issues at
    scale however.

    The methods from the BaseDataIngestionEngine that are overwritten for functionality
    are:

        * _add_session_web_obj
        * _get_validation_status

    Args:

        db_uri (str): The string URI for the database to be connected to. It is
            used to initialize the SQLAlchemy database engine.

        WebPageResponseObjs (BaseWebPageResponse): Arguments that are assumed
            (and type checked) to be instances of BaseWebPageResponse() objects or
            any object that uses BaseWebPageResponse() as its base.

    Attributes:

            _WebPageResponseObjs (list): A list of arguments that are assumed (and type
                checked) to be instances of BaseWebPageResponse() objects or any object
                that uses BaseWebPageResponse() as its base.

            _db_uri (str): The URI of the database used to initialize the SQLA engine.

            _sqlaengine (sqlalchemy.engine.Engine): The SQLAlchemy engine object that
                is used to represent and interact with the database. The database
                engine is initialized by the URI passed as the db_uri argument.

            _db_session_maker (sqlalchemy.orm.session.sessionmaker): The object
                that configures the Session factory that is used to create Session()
                objects within the Ingestion engine.

            _db_session (sqlalchemy.orm.session.Session): A persistent database
                connection to the database binded to the database engine via the
                _sqlaengine parameter.

    """
    def __init__(self, db_uri, *WebPageResponseObjs):

        # Initalizing the Parent BaseWebPageIngestionEngine object:
        super().__init__(db_uri, *WebPageResponseObjs)

    def _add_session_web_obj(self, web_object):
        """
        The method serves to add an ingested WebPageResponse Object to the Ingestion
        Engines’ database session in the appropriate schema.

        This method overwrites the default implementation of the __add_session_web_obj
        method. Contrary to the established format of importing a SQLAlchemy db
        model and initializing an instance of said model with the fields extracted
        from the Web Object, this method makes use of the pandas library.

        The method uses the dataframe.to_sql method from the pandas library in order
        to write the holdings data extracted from the FundHoldingsResponse Objects
        to the connected database. The benefits and drawbacks of this method are
        described above in the Ingestion Engine’s documentation.

        Args:
            web_object (BaseWebPageResponse): An object containing the parameters
                to be added to the database session. Is assumed to be an instance
                of BaseWebPageResponse or object that uses BaseWebPageResponse as
                parent. It is validated via the internal validation methods. For
                this ingestion engine, it is assumed that the input WebResponseObjects
                are FundHoldingsResponseObjects.

        """
        # Extracting the validation of the web_object from the validation dict:
        if self._validation_dict[web_object] > 10:

            # Extracting the dataframe to be written to the db from the web_object:
            fund_holdings_df = web_object._holdings_data

            # Creating the database table name:
            fund_holdings_tbl_name = f"{web_object._ticker}_holdings_data"

            # Making use of the pandas library to write the dataframe to the database:
            fund_holdings_df.to_sql(
                fund_holdings_tbl_name, con=self._sqlaengine, if_exists='replace',
                index=True)

        else:
            raise ValueError(f"Object {web_object} Was Not Added to Session due to Validation Error")

    def _get_validation_status(self, obj):
        '''
        The validation method is extended from the Base Ingestion Engine to only
        validate WebPageResponse Objects that contain structured firm holdings
        data such as the NASDAQFundHoldingsResponseObject.

        It displays a status code above 20 if the object passed into the method
        is considered validated for the current Ingestion Engine. If the object
        is not conciderd validated then it returns a status code of 10.

        Args:

            obj (object): The object that is being validated.

        Returns:

            int: The status code generated by the object parameter.

        '''
        # Using basic conditional to screen for correct PageResponse Objects:
        if isinstance(obj, NASDAQFundHoldingsResponseObject):
            return 20

        else:
            return 10
