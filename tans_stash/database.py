from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

#path and name of the location when you need database
SQLACHEMY_DATABASE_URL = 'sqlite:///./pyconnectivity.db'

engine = create_engine(SQLACHEMY_DATABASE_URL, connect_args={'check_same_thread': False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()