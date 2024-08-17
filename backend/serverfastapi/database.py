import os
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import ProgrammingError

# DATABASE_URI = "sqlite:///./sql_app.db"
# DATABASE_URI = "postgresql://user:password@postgresserver/db"
MYSQL_USERNAME=os.environ['MYSQL_USERNAME']
MYSQL_PASSWORD=os.environ['MYSQL_PASSWORD']
MYSQL_HOST=os.environ['MYSQL_HOST']
MYSQL_PORT=os.environ['MYSQL_PORT']
MYSQL_DB_NAME=os.environ['MYSQL_DB_NAME']

DATABASE_URI=f'mysql+pymysql://{MYSQL_USERNAME}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}'

engine = create_engine(DATABASE_URI)

def create_database_if_not_exists(engine, database_name):
    # Connect to the MySQL server (without specifying a database)
    with engine.connect() as conn:
        try:
            # Try to create the database
            conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {database_name}"))
            print(f"Database '{database_name}' is ready.")
        except ProgrammingError as e:
            print(f"Failed to create database: {e}")

# Check and create the database if it doesn't exist
create_database_if_not_exists(engine, MYSQL_DB_NAME)

# Now, switch to the database
DATABASE_URI = f'mysql+pymysql://{MYSQL_USERNAME}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB_NAME}'
engine = create_engine(DATABASE_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
