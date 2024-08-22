# Legacy interface that may be useful for some legacy operations.
# To be integrated into the parent database interface class.

import os
from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import ProgrammingError, OperationalError
from sqlalchemy import text

class MySQLInterface:
    def __init__(self, force_recreate_db=False):
        self.MYSQL_USERNAME = os.environ['MYSQL_USERNAME']
        self.MYSQL_PASSWORD = os.environ['MYSQL_PASSWORD']
        self.MYSQL_HOST = os.environ['MYSQL_HOST']
        self.MYSQL_PORT = os.environ['MYSQL_PORT']
        self.MYSQL_DB_NAME = os.environ['MYSQL_DB_NAME']
        self.RECREATE_DB = os.getenv('RECREATE_DB', '0') == '1'
        if force_recreate_db:
            self.RECREATE_DB = True
        self.engine = self.create_engine_without_db()

    def create_engine_without_db(self):
        DATABASE_URI = f'mysql+pymysql://{self.MYSQL_USERNAME}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}'
        return create_engine(DATABASE_URI,
                    pool_size=10,
                    max_overflow=20,
                    pool_timeout=30,
                    pool_recycle=1800  # Recycle connections after 30 minutes
                )

    def create_engine_with_db(self):
        DATABASE_URI = f'mysql+pymysql://{self.MYSQL_USERNAME}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DB_NAME}'
        return create_engine(DATABASE_URI,
                    pool_size=10,
                    max_overflow=20,
                    pool_timeout=30,
                    pool_recycle=1800  # Recycle connections after 30 minutes
                )

    def recreate_database(self):
        with self.engine.connect() as conn:
            try:
                conn.execute(text(f"DROP DATABASE IF EXISTS {self.MYSQL_DB_NAME}"))
                print(f"Database '{self.MYSQL_DB_NAME}' has been dropped.")
            except ProgrammingError as e:
                print(f"Failed to drop database: {e}")

    def create_database_if_not_exists(self):
        with self.engine.connect() as conn:
            try:
                conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {self.MYSQL_DB_NAME}"))
                print(f"Database '{self.MYSQL_DB_NAME}' is ready.")
            except ProgrammingError as e:
                print(f"Failed to create database: {e}")

    def setup_database(self):
        if self.RECREATE_DB:
            self.recreate_database()
        self.create_database_if_not_exists()
        self.engine = self.create_engine_with_db()

    def create_tables(self, schema_file_path: str):
        with self.engine.connect() as conn:
            with open(schema_file_path, "r") as file:
                queries = file.read()
                for query in queries.split(';'):
                    if query.strip():
                        try:
                            conn.execute(text(query))
                            query_single_line = ' '.join(query.splitlines()).strip()
                            print(f"Executed: {query_single_line[:50]}...") # Print part of the query for confirmation
                        except (ProgrammingError, OperationalError) as e:
                            print(f"------> Failed to execute query: {e}")

    def get_session(self):
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        return SessionLocal()

    def fetch_data_from_db(self, query: str):
        """
        Fetch data from MySQL database based on the provided query.
        
        :param query: The SQL query to execute.
        :return: List of tuples representing the fetched rows.
        """
        with self.get_session() as session:
            result = session.execute(text(query)).fetchall()
            return [row for row in result]

# Example Usage
if __name__ == "__main__":
    mysql_interface = MySQLInterface(force_recreate_db=True)
    mysql_interface.setup_database()
    mysql_interface.create_tables("database/schemas.sql")
