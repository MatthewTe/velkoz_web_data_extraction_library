# Importing 3rd Party Packages:
from sqlalchemy import Column, Integer, String, Text, DateTime, LargeBinary
from sqlalchemy.ext.declarative import declarative_base

# Creating the declarative base object used to create base database orm models:
Base = declarative_base()

class NASDAQStockDataSummaryModel(Base):
    """
    # TODO: Paste Google Docs In-Line Documentation.
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
