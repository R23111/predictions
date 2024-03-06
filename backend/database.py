"""
This module provides the necessary components for working with the database.

The module sets up the database engine, session factory, and declarative base for defining database models.

"""

from sqlalchemy.ext.declarative import declared_attr

from sqlmodel import create_engine
from sqlmodel import SQLModel
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


from backend.core.config import settings

engine = create_engine(settings.DATABASE_URI, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base = declarative_base()

SQLModel.metadata = Base.metadata
SQLModel.metadata.create_all(engine)
