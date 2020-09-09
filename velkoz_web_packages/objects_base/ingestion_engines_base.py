# Importing native packages:
import time

# Importing thrid party packages:
from sqlalchemy import create_engine, MetaData, Column, String, DateTime, Integer
from sqlalchemy.orm import sessionmaker, Session

class BaseWebPageIngestionEngine(object):
    """
    A class representing the base object of a data ingestion engine.

    This is the Base class for the data ingestion engine. It represents a connection
    to a downstream database and is used to transform and write data extracted
    by a velkoz data object to any database it is connected. It performs writing
    to databases via the SQLAlchemy ORM.

    This object performs the same function as the BaseWebPageResponse() object. It
    serves as a base object for other custom data ingestion engines to be written.
    Ideally every new web scraping object that inherits from BaseWebPageResponse()
    should be written with an accompanying Ingestion Engine that Inherits from
    the BaseDataIngestionEngine().

    Args:
        db_uri (str): The string URI for the database to be connected to. It is
            used to initialize the SQLAlchemy database engine.

        *WebPageResponseObjs (list): A list of arguments that are assumed
            (and type checked) to be instances of BaseWebPageResponse() objects or
            any object that uses BaseWebPageResponse() as its base.

    Attributes:
            *_WebPageResponseObjs (list): A list of arguments that are assumed (and type
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
        * https://hackersandslackers.com/python-database-management-sqlalchemy


    Todo:
        * Create database connection methods with SQLA.
        * Write method for default data writing.
        * Determine if the self._validation_dict should use dict comprehension
            as opposed to calling function. (Have only one method __get_validation_status().)
        * Write tests for the Base Ingestion Engine.
    """

    def __init__(self, db_uri, *WebPageResponseObjs):

        # Declaring instance variables:
        self._WebPageResponseObjs = WebPageResponseObjs
        self._db_uri = db_uri

        # Creating the sqlalchemy database engine and binding session to database:
        self._sqlaengine = create_engine(self._db_uri, echo=True)
        self._db_session_maker = sessionmaker(bind=self._sqlaengine)
        self._db_session = Session()

        # Performing validation/type checking on the *_WebResponseObj arguments:
        self._validation_dict = self.__validate_args()

    def _default_write(self):
        '''
        # TODO: Add Documentation for _default_write() when __default_web_obj_write().
        '''
        pass

    def __default_web_obj_write(self, web_object):
        """The method ingests a web_object, validates said object and adds the
        default data parameters from BaseWebPageResponse() into the database session.

        The method validates the input web_object parameter. If the input is validated
        as an instance of BaseWebPageResponse() or an objects that inherits from
        BaseWebPageResponse() it then passes the default parameters associated with
        the BaseWebPageResponse() instance into a SQLA database table model. The
        BaseWebPageResponse() parameters that are passed into the SQLA db model are:

        * BaseWebPageResponse._initialized_time
        * BaseWebPageResponse._http_response
        * BaseWebPageResponse._url
        * BaseWebPageResponse._html_body

        These parameters of the BaseWebPageResponse object are used to initialize
        an instance of the SQLA BaseWebPageResponse Database Model. Once the database
        model has been initialized, the instance is added to the main db session.

        This method does not commit any data to the database, it only adds instances
        of a model to the core db.session. This is meant as the default method of
        writing Web Objects to a database. It is expected that any other ingestion
        engines that are written that use BaseDataIngestionEngine as a base do not
        use this implementation and either overwrite it or write a custom database
        write method.

        References:
            * https://hackersandslackers.com/sqlalchemy-data-models
            * https://docs.sqlalchemy.org/en/13/core/type_basics.html#sqlalchemy.types.PickleType
        
        Args:
            web_object (BaseWebPageResponse): An object containing the parameters
                to be added to the database session. Is assumed to be an instance
                of BaseWebPageResponse or object that uses BaseWebPageResponse as
                parent. It is validated.

        Todo:
            * Research How to structure a SQLA data model for ingesting BaseWebPageResponse
                objects.

            * Determine the html content extracted from the BaseWebPageResponse
                is to be stored as raw html content or as a pickled Soup objects.

        """
        # Validating input of web_object: # NOTE: More Pythonic to try-except instead of isinstance type-checking:
        try:

            # Ensuring that the response code a 200 status code:
            if  200 <= web_object._http_response.status_code <=300:

                # Creating custom table name based on the web_objects __str__ / __repr__ :
                table_name = web_object.__repr__().lower()





            else:
                pass

        except:
            pass

    def __validate_args(self):
        '''
        A method used to collect data on and type check the argumens passed into the
        *_WebPageResponseObjs parameter.

        The method at base ensures that each element passed into the *argument is
        either an instance of BaseWebPageResponse or one of its subclasses. It
        iterates through the list of _WebPageResponseObjs and converts each object
        into a status code (in the same manner as an HTTP Response status code)
        that indicate the validation status of the *_WebPageResponseObjs elements).
        It does this by calling the __get_validation_status() method for each object
        in the list.

        It then builds a dictionary of key-value pairs {object: object_status_code}.
        It builds a dictionary in order to associate the status_code with the object
        for debugging purposes in the event of an error.

        Returns:
            dict: The dictionary that contains the key-value pairs of
                {object: object_status_code} generated from the list of arguments
                passed into *_WebPageResponseObjs.

        '''
        # Iterating through the list of _WebPageResponseObjs and determining obj type:
        object_type_dict = {obj:self.__get_validation_status(obj) for obj in self._WebPageResponseObjs}

        return object_type_dict

    def __get_validation_status(self, obj):
        '''
        The method used to convert an object into a validation status code.

        It simply uses conditionals to determine which status code to return. Base
        on the type(obj).

        The current status codes supported are:

        20 : The object is a direct instance of BaseWebPageResponse object.
        21 : The object is an instance of a subclass of BaseWebPageResponse object.
        10 : The object is not an instance of the base or subclass
            of a BaseWebPageResponse object.

        Args:
            obj (object): The object that is being validated.

        Returns:
            int: The status code generated by the object parameter.

        '''

        # Conditionals that determine which status codes to return:
        # TODO: Incorporate Switches when more comprehensive validation status are developed:
        if isinstance(obj, BaseWebPageResponse):
            return 20

        else:
            return 10
