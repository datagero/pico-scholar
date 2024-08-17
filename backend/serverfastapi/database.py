import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# DATABASE_URI = "sqlite:///./sql_app.db"
# DATABASE_URI = "postgresql://user:password@postgresserver/db"
MYSQL_USERNAME=os.environ['MYSQL_USERNAME']
MYSQL_PASSWORD=os.environ['MYSQL_PASSWORD']
MYSQL_HOST=os.environ['MYSQL_HOST']
MYSQL_PORT=os.environ['MYSQL_PORT']
MYSQL_DB_NAME=os.environ['MYSQL_DB_NAME']

DATABASE_URI=f'mysql+pymysql://{MYSQL_USERNAME}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB_NAME}'

engine = create_engine(DATABASE_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
