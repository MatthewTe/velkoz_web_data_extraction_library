# Importing testing frameworks:
import unittest

# Importing 3rd party packages:
import bs4
import sqlite3
import sqlalchemy
import pandas as pd
import datetime
from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, BLOB, Table

# Importing Base Objects for testing:
from velkoz_web_packages.objects_base.db_orm_models_base import Base
from velkoz_web_packages.objects_base.web_objects_base import BaseWebPageResponse
from velkoz_web_packages.objects_base.ingestion_engines_base import BaseWebPageIngestionEngine



# Creating Several of the BaseWebPageResponse Default Objects for testing:
google = BaseWebPageResponse('https://www.google.com/')
stack_overflow = BaseWebPageResponse('https://stackoverflow.com/')
bing = BaseWebPageResponse('https://www.bing.com/')
wikipedia = BaseWebPageResponse('https://www.wikipedia.org/')

base_web_obj_lst = [google, stack_overflow, bing, wikipedia]

class BaseWebPageResponseTest(unittest.TestCase):

    # Method that tests the Base WebPageResponseObj requests.get:
    def test_base_web_object_response_obj(self):
        """
        The UnitTest Method that tests the BaseWebPageResponse.___http_response
        paramer.

        Tests the requests.get response object when a url is passed into the
        BaseWebPageResponse() object. The test asserts that the response from
        the GET request is an integer (requests.get.status_code). It is not
        concerned with the status of the response (200, 404, etc.). The test only
        assers if a response was recieved, meaning the GET request was sent out correctly.

        Note: The status code is assumed to be 200 due to the url's used being
            very concistent. As such an IsEqual value is asserted in addition to
            an integer type check.

        """

        # Iterating through base_web_obj_lst and creating list of status codes:
        status_code_lst = [web_obj._http_response.status_code for web_obj in base_web_obj_lst]

        # Iterating through the list of web obj status codes and asserting they are 200:
        assert_equal_lst = [
            self.assertEqual(status_code, 200) for status_code in status_code_lst
        ]

        # Iterating through the list of web objects testing for integer type:
        assert_type_lst = [
            self.assertIs(type(status_code), int) for status_code in status_code_lst
        ]

    # Method that tests the Base WebPageResponseObj's BeautifulSoup conctent:
    def test_base_web_object_bs4(self):
        """
        The UnitTest Method performs a test for sucessful extraction of a Bs4
        object.

        It performs an Assertion Test on the ._html_body parameter, testing if the
        extracted data was a bytes object. Once again the content is not being
        parsed, just the data type.

        """
        # Performing type testing for the html body of the BaseWebPageResponse:
        html_body_type_assertion = [

            self.assertIsInstance(web_obj._html_body, bytes) for web_obj in base_web_obj_lst
            ]

class BaseWebPageIngestionEngineTest(unittest.TestCase):
    """The test object that contains the unit & integration tests for the BaseWebPageIngestionEngine
    object.

    The object contains the methods that tests the following functionality of the
    BaseWebPageIngestionEngine:

    * 'test_db_base_ingestion()': The Ingestion Engine sucessfully connects to the
        database and creates the relevant database schema if it does not already
        exist and that the Ingestion Engine sucessfully writes the base
        parameters to the database using the correct data types and storage
        techniques.

    * 'test_ingestion_validation()': The Ingestion Engine validates the ingested
        BaseWebPageResponse objects accuratley, filtering out any Non BaseWebPageResponse
        objects passed into the Ingestion Engine.

    * 'test_ingestion_engine_web_obj_que()': The Ingestion Engine treats the
        *args of WebObjects passed into it as a de-facto 'que' of items. The
        args are stored as a list, and elements can be added and removed via
        Ingestion Engine methods. The writing of data to a database also purges
        the que of all objects that are sucessfully written to a database.

    """
    def test_db_base_ingestion(self):
        """The method tests the creation of the BaseWebPageIngestionEngine's
        database connection.

        The method tests the creation of the Ingestion Engine's sqlalchemy
        database engine and session by initalizing an instance of the
        BaseWebPageIngestionEngine and tests the instance parameters of said object.

        It then writes data to the in-memory database using the base_write methods.
        This data is then read from the database and type checked to insure that
        the base BaseWebPageResponse parameters are written in to the database
        correctly.

        """
        # Creating the database URI for an in-memory database:
        self.in_memory_uri = "sqlite:///:memory:"

        # Creating the instance of the Ingestion Engine:
        ingestion_engine = BaseWebPageIngestionEngine(
            self.in_memory_uri, google, stack_overflow)

        # Performing basic type checking for sql engine and session instance params:
        self.assertIsInstance(ingestion_engine._sqlaengine, sqlalchemy.engine.Engine)
        self.assertIsInstance(ingestion_engine._db_session_maker, sqlalchemy.orm.session.sessionmaker)
        self.assertIsInstance(ingestion_engine._db_session, sqlalchemy.orm.scoped_session)

        # Performing the base database writing methods for the BaseDataIngestionEngine:
        ingestion_engine._write_web_objects()

        # Testing that the correct table schema has been created via the Ingestion Engine's
        # BaseWebPageResponseModel database model:
        self.assertIn('default_web_obj_tbl', Base.metadata.tables.keys())

        # Extracting the default web object table from the database to test datatypes:
        web_object_data = pd.read_sql_table(
            'default_web_obj_tbl',
            con = ingestion_engine._sqlaengine,
            )

        # Iterating through the web_objects_data queried and type checking:
        for index, row in web_object_data.iterrows():

            # Asserting the types for each model field:
            self.assertIsInstance(row['date_initialized'], datetime.datetime) # 'date_initialized'
            self.assertIsInstance(row['response_code'], int) # 'response_code'
            self.assertIsInstance(row['url'], str) # 'url'
            self.assertIsInstance(row['html_content'], bytes) # 'html_content'

    def test_ingestion_validation(self):
        """
        The method tests the validation methods of the Base Ingestion Engine.

        The tests passes four BaseWebPageResponse objects that should be validated
        by the Eninge. it also passes three objects that should not be validated
        by the ingestion engine.

        Assertion tests are then used to validate that objects are correctly
        validated and processed by the BaseDataIngestionEngine.__validate_args()
        validation method.
        """
        bool_obj = True
        string_obj = "Test_String"
        float_obj = 10023.453

        # Creating Ingestion Engine Object:
        ingestion_engine = BaseWebPageIngestionEngine("sqlite:///:memory:",
            google, bing, wikipedia, bool_obj, string_obj, float_obj)

        # Extracting internal paramer 'validation_dict' via '_validate_args' method:
        obj_validation_dict = ingestion_engine._validate_args()

        # Performing assertion tests to compare the status codes assigned by the validation method:

        # Objects that should be validated as the Base WebObject type:
        self.assertEqual(obj_validation_dict[google], 20)
        self.assertEqual(obj_validation_dict[bing], 20)
        self.assertEqual(obj_validation_dict[wikipedia], 20)

        # Objects that should be validated as wholy incorrect types:
        self.assertEqual(obj_validation_dict[bool_obj], 10)
        self.assertEqual(obj_validation_dict[string_obj], 10)
        self.assertEqual(obj_validation_dict[float_obj], 10)

    def test_ingestion_engine_web_obj_que(self):
        """The method tests the mutability of the _WebResponseObj list of items.

        The method initializes an ingestion engine object with several BaseWebPageResponse
        objects and performs various assertion tests that check the length of the
        _WebResponseObj list and ensure that the list remains at the correct
        length with the correct objects within it.

        """
        # Creating Ingestion Engine Object:
        ingestion_engine = BaseWebPageIngestionEngine("sqlite:///:memory:")

        # Asserting the length of the _WebResponseObj list (should be 0):
        self.assertEqual(len(ingestion_engine._WebPageResponseObjs), 0)

        # Iterating over a list of web objects and adding them to the ingestion engine:
        for web_obj in base_web_obj_lst:
            ingestion_engine._insert_web_obj(web_obj)

        # Asserting the new length of the _WebResponseObj list (should be 4):
        self.assertEqual(len(ingestion_engine._WebPageResponseObjs), 4)

        # Removing several elements from the _WebResponseObj list:
        ingestion_engine._WebPageResponseObjs.remove(bing)
        ingestion_engine._WebPageResponseObjs.remove(wikipedia)

        # Asserting the new length of the _WebResponseObj list (should be 2):
        self.assertEqual(len(ingestion_engine._WebPageResponseObjs), 2)

        # Writing all remaining elements to an in-memory database:
        ingestion_engine._write_web_objects()

        # Asserting the length of the _WebResponseObj list (should now be empty):
        self.assertEqual(len(ingestion_engine._WebPageResponseObjs), 0)
