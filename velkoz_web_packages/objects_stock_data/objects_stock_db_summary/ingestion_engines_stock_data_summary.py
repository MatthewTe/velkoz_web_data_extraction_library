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
    # TODO: Paste Google Docs In-Line Documentation
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

        # Query a list of all table names that exist in the database:
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
        # TODO: Add Documentation.
        """
        # Ensuring that the web object has been validated for ingestion:
        if self._validation_dict[web_object] > 10:

            # Creating all tables associated with the SQLAlchemy Base Database Modle:
            Base.metadata.create_all(self._sqlaengine)

            # Searching the existing datbase tables for existing stock data tables:
            ticker_value_dict = self._search_database_table_set(web_obj, self._existing_db_tables)

            # If the existing row query returns nothing model instance is initialized
            # and to the database session:
            if existing_ticker_row is None:

                # Initialize db model:
                ticker_summary_instance = NASDAQStockDataSummaryModel(
                    ticker = web_obj,
                    price_tbl = ticker_value_dict['price_tbl'],
                    holdings_tbl = ticker_value_dict['holdings_tbl'],
                    last_updated = ticker_value_dict['last_updated']
                    )

                # Adding database model to session:
                self._db_session.add(ticker_summary_instance)

            # If the existing row query exists overwrite its parameters w/ recent info:
        elif existing_ticker_row != None:
                # Updating parameters for existing database model instance:
                existing_ticker_row.update(ticker_value_dict)

    def _search_database_table_set(self, ticker, tbl_set):
        """
        input --> ticker string, a table set.

        output --> {
            "price_tbl" : 'NaN' / 'f"{web_obj}_price_history"'
            "holdings_tbl" : 'NaN' / f"{web_obj}_holdings_data"
            "last_updated" : datetime.datetime.now()
        }

        # TODO: Add Documentation
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
        # TODO: Write Docs.
        """
        # Ensuring that the ingested object is a string and a valid ticker by
        # initalizing a yh finance object:
        if type(obj) == str and len(yf.Ticker(obj).history(period='max')) != 0:
            return 20

        else:
            return 10
