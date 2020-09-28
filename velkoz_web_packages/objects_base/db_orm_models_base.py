# Importing the database orm management packages:
from sqlalchemy import Column, Integer, String, Text, DateTime, LargeBinary
from sqlalchemy.ext.declarative import declarative_base

# Creating the declarative base object used to create base database orm models:
Base = declarative_base()

class BaseWebPageResponseModel(Base):
    """This is the database model that represents the database table for the
    BaseWebPageResponse object.

    This is the orm model that the BaseDataIngestionEngine uses to write base data
    extracted from each BaseWebPageResponse object into a database. The data model
    is designed to represent the following data from the BaseWebPageResponse object:

    * The time the BaseWebPageResponse object was initialized.
    * The http response code retrieved from the url of the BaseWebPageResponse object_url.
    * The url used to initialize the BaseWebPageResponse object.
    * The raw html content scraped from the site by the BaseWebPageResponse object.

    It is expected that WebObjects and Ingestion Engines that inherit from their
    base objects use a custom response model another method of writing data to
    a database.

    Attributes:

        __tablename__ (str): A metadata attribute that determines the name of the table
                created by the engine.

        date (sqlalchemy.Column): The Datetime that the BaseWebPageResponse
            object being ingested was created.

        response_code (sqlalchemy.Column): The http response Integer the BaseWebPageResponse
            object got from the url it was initialized with.

        url (sqlalchemy.Column): The url string that was used to initialize the
            BaseWebPageResponse object stored as Text.

        html_content (sqlalchemy.Column): The LargeBinary element used to store the
            raw html data scraped from the webpage by the BaseWebPageResponse object.
    """
    # Declaring table metadata attributes:
    __tablename__ = "default_web_obj_tbl"

    # Declaring table column attributes:
    date = Column(
        "date_initialized",
        DateTime,
        primary_key = True
    )
    response_code = Column(
        "response_code",
        Integer
    )
    url = Column(
        "url",
        Text
    )
    html_content = Column(
        "html_content",
        LargeBinary,
        nullable = True
    )

    # __dunder methods:
    def __repr__(self):

        return f"BaseWebPageResponse Model({self.url}_{self.date}_{self.response_code})"
