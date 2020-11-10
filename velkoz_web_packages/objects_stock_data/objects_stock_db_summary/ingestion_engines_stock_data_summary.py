# Importing native packages:
import time
import warnings
import datetime

# Importing Base Ingestion Engine Objects:
from velkoz_web_packages.objects_base.ingestion_engines_base import BaseWebPageIngestionEngine

# Importing the SQLAlchemy database model and model base:
from velkoz_web_packages.objects_stock_data.objects_stock_db_summary.db_orm_models_stock_data_summary import Base, NASDAQStockDataSummaryModel

# Importing thrid party packages:
from sqlalchemy import create_engine, MetaData, Column, String, DateTime, Integer, inspect
from sqlalchemy.orm import sessionmaker, Session, scoped_session
import yfinance as yf

class StockDataSummaryIngestionEngine(BaseWebPageIngestionEngine):
    """
    This ingestion engine is the engine responsible for generating and maintaining
    the “Stock Data Summary Table” within the connected database.

    Unlike many other Ingestion Engines it does not ingest a WebPageResponse
    object but instead ingests a string representing the ticker symbol in question.
    This ingestion engine is less of a web-scraping-data ingestion object and more
    of an object that is designed to perform its own generation of data based on
    the internal meta-data of the database it is connected to. As such all of the
    logic for generating data to be written to a database is stored within the
    ingestion engine.

    This is compared to other ingestion engines where the engine only contains
    minimal logic for data writing and simply serves as a database entry point
    for the objects that contain the main data extraction logic and writable data,
    the WebPageResponse objects. This is done because this ingestion engine deals
    with only data that is internal to the current database. It compiles and writes
    data related to the data that is stored within the database associated with each
    ticker symbol that is passed into it.

    It does extend the BaseWebPageIngestionEngine and overwrites these methods:

    * _write_web_objects
    * _add_session_web_obj
    * _get_validation_status

    The * args of WebPageResponseObjs are simply strings (eg "TSLA") instead of
    WebPageResponsebjects that are passed into the parent Base Ingestion Engine.

    Args:

        db_uri (str): The string URI for the database to be connected to. It is
            used to initialize the SQLAlchemy database engine.

        WebPageResponseObjs (Str): Arguments that are ticker strings. Presumably
            of stocks whose tickers are already being maintained within the
            connected databae.

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

        # Initalizing parent Ingestion Engine:
        super().__init__(db_uri, *WebPageResponseObjs)

    def _write_web_objects(self):
        """The method that writes data from the WebPageResponseObj passed into the
        ingestion engine using the default ingestion format.

        It first performs validation for the list of base web objects by calling
        the self._validate_args() method and declares the resulting dict as an
        instance parameter.

        It iterates through the web objects that have been passed into the ingestion
        engine and performs data ingestion operations on each web object by calling
        the __add_session_default_web_obj on each web_object. Once the web object
        is added to the session, it is removed from the list of WebObjects. The
        base implementation is overwritten for the NASDAQStockDataSummaryIngestionEngine
        in order to add a Query to the database fro a list of all existing table
        names. This is a parameter that is used in the logic of the _add_session_web_obj()
        internal method.

        This allows the list of WebObjects passed into the Ingestion Engine to
        essentally behave as a Que of WebObjects. Once all web object are sucessfully
        commited to a database, the que of Web Objects is emptied via the _purge_web_obj_que()
        method.

        As such, any WebObjects within the que will be removed after this method
        is called only if their data is sucessfully written to the database.

        """
        # Performing validation/type checking on the *_WebResponseObj arguments:
        self._validation_dict = self._validate_args()

        # Query a list of all table names that exist in the database from new SQLA engine:
        self._existing_db_tables = set(self._sqlaengine.table_names())

        # Iterating through the list of web objects adding them to the db session:
        for web_object in self._WebPageResponseObjs:

            # Adding them to the database session:
            self._add_session_web_obj(web_object)

            # Writing the web objects to the database.
            self._db_session.commit()

        # If all web objects are sucessfully added to the session, purging the que:
        self._purge_web_obj_que()

    def _add_session_web_obj(self, web_object):
        """
        The method ingests a web_object (in this case a ticker symbol) from the
        ingestion engines’ internal que and adds said object to the database
        session until it is written to the database via a session.commit method
        call that is located in the parent method “_write_web_objects”.

        The method first ensures that the input object has been validated by the
        engine’s internal validation methods. Once it has been validated the logic
        that adds the ticker symbol to the database is executed:

        - The database table described by the associated ORM model
            (NASDAQStockDataSummaryModel) is created if it does not already exist
            in the database.

        - Another method “_search_database_table_set” is called with the ticker
            symbol which searches a list of all table names within the connected
            database for the relevant information, which it returns in a dictionary.
        - The database is queried for an existing instance of the database model
            (if there already exists a data table row with this ticker).

        - If an existing row is found then that row is updated with the new data
            contained in the “_search_database_table_set” dictionary. If no existing
            row is found then a new model instance is created using said dictionary.
            In either cases, the new data is then added to the database session.

        Args:
            web_object (str): In this ingestion engine this web object is a ticker
                string that represents a stock ticker that is already being maintained
                in the database.

        References:

            * https://www.tutorialspoint.com/sqlalchemy/sqlalchemy_orm_updating_objects.htm

        """
        # Ensuring that the web object has been validated for ingestion:
        if self._validation_dict[web_object] > 10:

            # Creating all tables associated with the SQLAlchemy Base Database Modle:
            Base.metadata.create_all(self._sqlaengine)

            # Searching the existing datbase tables for existing stock data tables:
            ticker_value_dict = self._search_database_table_set(web_object, self._existing_db_tables)

            # Querying the database for a potential instance of the data model
            # (database table 'nasdaq_stock_data_summary_tbl' row):
            existing_ticker_row = self._db_session.query(
                NASDAQStockDataSummaryModel).filter_by(ticker=web_object).first()

            # If the existing row query returns nothing model instance is initialized
            # and to the database session:
            if existing_ticker_row is None:

                # Initialize db model:
                ticker_summary_instance = NASDAQStockDataSummaryModel(
                    ticker = web_object,
                    price_tbl = ticker_value_dict['price_tbl'],
                    holdings_tbl = ticker_value_dict['holdings_tbl'],
                    last_updated = ticker_value_dict['last_updated'])

                # Adding database model to session:
                self._db_session.add(ticker_summary_instance)

            # If the existing row query exists overwrite its parameters w/ recent info:
            else:

                # Updating parameters for existing database model instance:
                existing_ticker_row.price_tbl = ticker_value_dict['price_tbl']
                existing_ticker_row.holdings_tbl = ticker_value_dict['holdings_tbl']
                existing_ticker_row.last_updated = ticker_value_dict['last_updated']

                # Adding database model to session:
                self._db_session.commit()


    def _search_database_table_set(self, ticker, tbl_set):
        """This method searches a set of strings for specific strings that are
        based on the input ticker and internal formatted strings.

        The method was written to search a set containing all of the existing
        tables of the connected database for database tables associated with the
        input ticker symbol. Ticker associated data tables that are found are then
        written into a dictionary. If these tables are not found then a value of
        “NaN” is written to the dictionary. The database tables that are searched
        for in the input "tbl_set" are as follows:

        - ticker_price_history --> The time series stock price history for the ticker.
        - ticker_holdings_data --> The top 10 fund holdings table for the ticker.

        Args:
            ticker (str): The ticker string that is used to format all of the
                search strings that are used to parse the input set.

            tbl_set (set): A set containing strings representing the names of
                existing tables in the database that are searched by the method.

        Returns:
            dict : The dictionary containing the status of each ticker associated
                database table. It is in the format of:

                {
                    "price_tbl" : 'NaN' / 'f"{web_obj}_price_history"'
                    "holdings_tbl" : 'NaN' / f"{web_obj}_holdings_data"
                    "last_updated" : datetime.datetime.now()
                }

        """
        # Creating the main dict of values to be populated:
        db_values_dict = {
            "price_tbl" : "NaN",
            "holdings_tbl" : "NaN",
            "last_updated" : datetime.datetime.now()
            }

        # Searching the set for existing stock database tables to update values:
        if f"{ticker}_price_history" in tbl_set:
            db_values_dict['price_tbl'] = f"{ticker}_price_history"

        if f"{ticker}_holdings_data" in tbl_set:
            db_values_dict['holdings_tbl'] = f"{ticker}_holdings_data"

        return db_values_dict

    def _get_validation_status(self, obj):
        """
        The validation method ingests an object and returns an integer that indicates
        the validation status of the object.

        In this ingestion engine the validation method validates object strings
        that are determined to be valid stock tickers on the NASDAQ Exchange. As
        per the standard any integer > 10 is considered successfully validated.

        The method validates the object by ensuring that the object is a string
        data type and that the string successfully initialized the Ticker object
        from the yahoo finance python package. These two conditionals should
        indicate that the input object is a valid stock ticker.

        Args:
            obj (str): A string representing a ticker string presumably of stocks
                whose tickers are already being maintained within the connected database.

        Returns:
            int: The integer representing the validation status of the input object.
        """
        # Ensuring that the ingested object is a string and a valid ticker by
        # initalizing a yh finance object:
        if type(obj) == str and len(yf.Ticker(obj).history(period='max')) != 0:
            return 20

        else:
            return 10
