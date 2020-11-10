# Importing 3rd Party Packages:
from sqlalchemy import Column, Integer, String, Text, DateTime, LargeBinary
from sqlalchemy.ext.declarative import declarative_base

# Creating the declarative base object used to create base database orm models:
Base = declarative_base()

class NASDAQStockDataSummaryModel(Base):
    """The NASDAQStockDataSummaryModel is the SQLAlchemy model that represents
    the database table for storing Stock Summary Data that is compiled and ingested
    via the StockDataSummaryIngestionEngine.

    In the database each row is meant to represent all of the metadata about all
    associated data stored within the database about a single ticker.

    Attributes:
        __tablename__ (str): A metadata attribute that determines the name of the table
            created by the engine.

        __table_args__ (str): A metadata attribute that determines how the model
            interacts with an existing equivalent databaset table that already
            exists. In this case it is set to utilize any already existing database
            table with the same name.

        ticker (sqlalchemy.Column): The model parameter associated with the ticker
            column in the database. This is the primary key for the database.

        price_tbl (sqlalchemy.Column): The parameter associated with the 'price_tbl'
            column in the database. If no data table is found in the database that
            contains price data for a specific ticker is found then a 'NaN' value
            is written to this cell.

        holdings_tbl (sqlalchemy.Column): The parameter associated with the 'holdings_tbl'
            column in the database. If no data table is found in the database that
            contains holdings data for a specific ticker is found then a 'NaN' value
            is written to this cell.

        last_updated (sqlalchemy.Column): The parameter associated with a datetime
            column in the database. This represents the last time the database was
            searched for data associated with the ticker symbol. 
    """
    # Declaring table meta-data:
    __tablename__ = "nasdaq_stock_data_summary_tbl"
    __table_args__ = {'useexisting': True}

    # Declaring the table schema:
    ticker = Column(
        'ticker',
        String(20),
        primary_key = True,
        index = True)

    price_tbl = Column(
        'price_tbl',
        String(20),
        nullable = True)

    holdings_tbl = Column(
        'holdings_tbl',
        String(20),
        nullable = True)

    last_updated = Column(
        'last_updated',
        DateTime,
        nullable = True)

    # Dunder Methods:
    def __repr__(self):
        return f"NASDAQStockDataSummaryModel({self.ticker})"
