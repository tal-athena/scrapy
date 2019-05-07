#! -*- coding: utf-8 -*-

from sqlalchemy import create_engine, Column, Integer, Float, String, Boolean, BigInteger, Text, DateTime, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.engine.url import URL
import gba.settings
from sqlalchemy import event
from sqlalchemy import DDL
import datetime
import os

DeclarativeBase = declarative_base()


def db_connect():
    """Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance.
    """

    # return create_engine(URL(**settings.DATABASE))
    return create_engine('{driver}:///{database}'.format(driver=gba.settings.DATABASE["drivername"], database=gba.settings.DATABASE["database"]))


def create_tables(engine):
    """"""
    DeclarativeBase.metadata.create_all(engine)

class GbaData(DeclarativeBase):

    __tablename__ = "Records"

    ID = Column( 'Id', Integer, primary_key=True, autoincrement=True )
    PdfLink = Column('PdfLink', Text())
    PdfText = Column('PdfText', Text())
    DocumentUrl = Column('DocumentUrl', Text() )
    
    # __table_args__ = ( UniqueConstraint('ItemNumber', name='_item_number'), )
