# Importing native packages:
import time
import warnings

# Importing local packages:
from velkoz_web_packages.objects_base.web_objects_base import BaseWebPageResponse
from velkoz_web_packages.objects_base.db_orm_models_base import BaseWebPageResponseModel, Base

# Importing thrid party packages:
from sqlalchemy import create_engine, MetaData, Column, String, DateTime, Integer, inspect
from sqlalchemy.orm import sessionmaker, Session, scoped_session


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

        *WebPageResponseObjs (BaseWebPageResponse): Arguments that are assumed
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
        * Add 'Insert' method to add WebPageResponseObjs to Que
    """

    def __init__(self, db_uri, *WebPageResponseObjs):

        # Declaring instance variables:
        self._WebPageResponseObjs = list(WebPageResponseObjs)

        self._db_uri = db_uri

        # Creating the sqlalchemy database engine and binding session to database:
        self._sqlaengine = create_engine(self._db_uri, pool_pre_ping=True, echo=True)
        self._db_session_maker = sessionmaker(bind=self._sqlaengine)
        self._db_session = scoped_session(self._db_session_maker)

    def _insert_web_obj(self, web_obj):
        """The method contains the basic logic that allows a Web Object to be added
        to the que (list) of Web Objects currently in the ingestion engine.

        The method takes the parameter passed into it and validates said object
        according to the internal __get_validation_status() method. Once the object
        has been validated internally (if it passes the validation tests) it is
        then appended to the instance list self._WebPageResponseObjs

        """
        # Validating the input parameter:
        validation_status_code = self.__get_validation_status(web_obj)

        # If the input parameter is validated, appending it to the main Web Obj Que:
        if validation_status_code > 10:
            self._WebPageResponseObjs.append(web_obj)

        else:
            raise ValueError("Input Parameters Failed Internal Validation")

    def _purge_web_obj_que(self):
        """The method purges the list of web objects stored within the Ingestion
        Engine.

        When the method is called, it modifies the instance of the Web Object List
        by calling the clear() method on the parameter self._WebPageResponseObjs.

        """
        # Performing the clear method on the main Web Object Que:
        self._WebPageResponseObjs.clear()

    def _write_web_objects(self):
        """The method that writes data from the WebPageResponseObj passed into the
        ingestion engine using the default ingestion format.

        It first performs validation for the list of base web objects by calling
        the self._validate_args() method and declares the resulting dict as an
        instance parameter.

        It iterates through the web objects that have been passed into the ingestion
        engine and performs data ingestion operations on each web object by calling
        the __add_session_default_web_obj on each web_object. Once the web object
        is added to the session, it is removed from the list of WebObjects.

        This allows the list of WebObjects passed into the Ingestion Engine to
        essentally behave as a Que of WebObjects. Once all web object are sucessfully
        commited to a database, the que of Web Objects is emptied via the _purge_web_obj_que()
        method.

        As such, any WebObjects within the que will be removed after this method
        is called only if their data is sucessfully written to the database.

        """
        # Performing validation/type checking on the *_WebResponseObj arguments:
        self._validation_dict = self._validate_args()

        # Iterating through the list of web objects adding them to the db session:
        for web_object in self._WebPageResponseObjs:

            # Adding them to the database session:
            self.__add_session_web_obj(web_object)

            # Writing the web objects to the database.
            self._db_session.commit()

        # If all web objects are sucessfully added to the session, purging the que:
        self._purge_web_obj_que()

    def __add_session_web_obj(self, web_object):
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

        """
        # Ensuring that the web object has been validated:
        if self._validation_dict[web_object] > 10:

            # Initalizing an instance of the BaseWebPageResponseModel DB model:
            Base.metadata.create_all(self._sqlaengine)

            # Creating instance of the BaseWebPageResponseModel:
            web_obj_model_instance = BaseWebPageResponseModel(
                date = web_object._initialized_time,
                response_code = web_object._http_response.status_code,
                url = web_object._url,
                html_content = web_object._html_body)

            # Adding instance of BaseWebPageResponseModel to the DB session:
            self._db_session.add(web_obj_model_instance)

        else:
            raise ValueError(f"Object {web_object} Was Not Added to Session")
            

    def _validate_args(self):
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
