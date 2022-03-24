from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import config


engine = create_engine(config.DB_URI, echo=config.VERBOSE)
Base = declarative_base()


def get_session():
    session = sessionmaker(bind=engine)
    return session()


def create_db():
    Base.metadata.create_all(engine)
