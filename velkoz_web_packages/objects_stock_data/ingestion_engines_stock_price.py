# Importing native packages:
import time
import warnings

# Importing Base Ingestion Engine Objects:
from velkoz_web_packages.objects_base.ingestion_engines_base import BaseWebPageIngestionEngine
from velkoz_web_packages.objects_stock_data.web_objects_stock_price import NASDAQStockPriceResponseObject


# Importing thrid party packages:
from sqlalchemy import create_engine, MetaData, Column, String, DateTime, Integer, inspect
from sqlalchemy.orm import sessionmaker, Session, scoped_session

class StockPriceDataIngestionEngine(BaseWebPageIngestionEngine):
    """
    This is the Data Ingestion Engine that is used to write WebPageResponse Objects
    relating to stock price data to a database.

    The IngestionEngine extends/overwrites the BaseWebPageIngestionEngine and is
    designed to be compatible with WebPageResponse Objects that extract stock price
    data in the format of StockPriceRespose Objects like the NASDAQStockPriceResponseObject.
    It performs data validation for Response Objects that are passed into it to
    ensure this compatibility.

    The main database ingestion methods within the Ingestion Engine are overwritten
    to facilitate the new data structures of the ingested StockPriceResponse Objects
    and their corresponding schema. Due to the inherent simplicity of representing
    time series price data, the primary methods of database ingestion can be outsourced
    to the pandas library, namely the database writing methods associated with writing pandas
    dataframes to a database via an SQLAlchemy engine. The methods from the
    BaseDataIngestionEngine that are overwritten for functionality are:

    * __add_session_web_obj
    * __get_validation_status

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

    References:

        * https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.to_sql.html

    """
    def __init__(self, db_uri, *WebPageResponseObjs):

        # Initalizing the Parent BaseWebPageIngestionEngine object:
        super().__init__(db_uri, *WebPageResponseObjs)

    def __add_session_web_obj(self, web_object):
        """
        The method serves to add an ingested WebPageResponse Object to the Ingestion
        Engines’ database session in the appropriate schema.

        This method overwrites the default implementation of the __add_session_web_obj
        method. Contrary to the established format of importing a SQLAlchemy db
        model and initializing an instance of said model with the fields extracted
        from the Web Object, this method makes use of the pandas library.

        Due to the method only being designed to write time series price history
        data stored as a field in a StockPriceResponse Object it makes use of
        the pandas DataFrame.to_sql functionality that allows a pandas dataframe
        to be written to a database.

        This means that the method does not have to rely on a custom database
        model and only has to correctly configure the pandas dataframe writing
        method via meta-data extracted from the ingested StockPriceResponse Object.
        For simplicity’s sake, once the price history of a specific ticker is added
        to the database session and is to be written to the database, if an existing
        price-history table exists in the database it is dropped and the new tabel
        is written in its place.

        At scale this is expected to have serious performance
        costs however it is the most simplistic method of maintaining an up-to-date
        price history for an individual ticker.

        Args:
            web_object (BaseWebPageResponse): An object containing the parameters
                to be added to the database session. Is assumed to be an instance
                of BaseWebPageResponse or object that uses BaseWebPageResponse as
                parent. It is validated.

        """
        # Ensuring that the Web Object has been validated:
        if self._validation_dict[web_object] > 10:

            # Extracting the dataframe from the web object:
            price_df = web_object._price_history_full
            price_df_tbl_name = f"{web_object._ticker}_price_history"

            # Writing the price dataframe to the database:
            price_df.to_sql(
                price_df_tbl_name, con=self._db_session, if_exists='replace',
                index=True)

        else:
            raise ValueError(f"Object {web_object} Was Not Added to Session due to Validation Error")

    def __get_validation_status(self, obj):
        '''
        The validation method is extended from the Base Ingestion Engine to only
        validate WebPageResponse Objects that contain structured time series price
        data such as the NASDAQStockPriceResponseObject.

        It displays a status code above 20 if the object passed into the method
        is considered validated for the current Ingestion Engine. If the object
        is not conciderd validated then it returns a status code of 10.

        Args:

            obj (object): The object that is being validated.

        Returns:

            int: The status code generated by the object parameter.

        '''
        # Using basic conditional to screen for correct PageResponse Objects:
        if isinstance(NASDAQStockPriceResponseObject, obj):
            return 20

        else:
            return 10
