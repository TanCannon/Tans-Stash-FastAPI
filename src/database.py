'''------------- SQLITE connectivity ---------------- '''
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base

from src.core.settings import settings

#path and name of the location when you need database
SQLACHEMY_DATABASE_URL = settings.DATABASE_URL

engine = create_engine(SQLACHEMY_DATABASE_URL, connect_args={'check_same_thread': False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

''' ----------- MYSQL connectivity ---------------- '''
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker, declarative_base

# SQLALCHEMY_DATABASE_URL = "mysql+pymysql://root:Tanmaya#2003@localhost:3306/tans_stash"

# engine = create_engine(
#     SQLALCHEMY_DATABASE_URL,
#     pool_pre_ping=True  # avoids MySQL timeout issues
# )

# SessionLocal = sessionmaker(
#     autocommit=False,
#     autoflush=False,
#     bind=engine
# )

# Base = declarative_base()