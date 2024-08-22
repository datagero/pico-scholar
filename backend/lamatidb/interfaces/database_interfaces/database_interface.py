## Newer interface that aims to encapsulate both MySQL and TiDB interfaces.
## To be divided into inherent classes for MySQL and TiDB, to manage operational/ingestion data and vectors/indixes respectively.

from sqlalchemy import create_engine, text, URL
from sqlalchemy.orm import sessionmaker
import os

class DatabaseInterface:
    def __init__(self, db_type: str, db_name: str, force_recreate_db=False):
        self.db_type = db_type.lower()  # Either 'mysql' or 'tidb'
        self.db_name = db_name
        self.force_recreate_db = force_recreate_db

        if self.db_type == 'mysql':
            self.DB_USERNAME = os.environ['MYSQL_USERNAME']
            self.DB_PASSWORD = os.environ['MYSQL_PASSWORD']
            self.DB_HOST = os.environ['MYSQL_HOST']
            self.DB_PORT = os.environ['MYSQL_PORT']
        elif self.db_type == 'tidb':
            self.DB_USERNAME = os.environ['TIDB_USERNAME']
            self.DB_PASSWORD = os.environ['TIDB_PASSWORD']
            self.DB_HOST = os.environ['TIDB_HOST']
            self.DB_PORT = int(os.environ['TIDB_PORT'])
        else:
            raise ValueError("Unsupported database type. Use 'mysql' or 'tidb'.")

        self.engine = self.create_engine_without_db()

    def create_engine_without_db(self):
        if self.db_type == 'mysql':
            DATABASE_URI = f'mysql+pymysql://{self.DB_USERNAME}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}'
        elif self.db_type == 'tidb':
            DATABASE_URI = URL(
                "mysql+pymysql",
                username=self.DB_USERNAME,
                password=self.DB_PASSWORD,
                host=self.DB_HOST,
                port=self.DB_PORT,
                database='mysql',
                query={"ssl_verify_cert": True, "ssl_verify_identity": True},
            )
        return create_engine(DATABASE_URI, pool_size=10, max_overflow=20, pool_timeout=30, pool_recycle=1800)

    def create_engine_with_db(self):
        if self.db_type == 'mysql':
            DATABASE_URI = f'mysql+pymysql://{self.DB_USERNAME}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.db_name}'
        elif self.db_type == 'tidb':
            DATABASE_URI = URL(
                "mysql+pymysql",
                username=self.DB_USERNAME,
                password=self.DB_PASSWORD,
                host=self.DB_HOST,
                port=self.DB_PORT,
                database=self.db_name,
                query={"ssl_verify_cert": True, "ssl_verify_identity": True},
            )
        return create_engine(DATABASE_URI, pool_size=10, max_overflow=20, pool_timeout=30, pool_recycle=1800)

    def recreate_database(self):
        with self.engine.connect() as conn:
            try:
                conn.execute(text(f"DROP DATABASE IF EXISTS {self.db_name}"))
                print(f"Database '{self.db_name}' has been dropped.")
            except Exception as e:
                print(f"Failed to drop database: {e}")

    def create_database_if_not_exists(self):
        with self.engine.connect() as conn:
            try:
                conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {self.db_name}"))
                print(f"Database '{self.db_name}' is ready.")
            except Exception as e:
                print(f"Failed to create database: {e}")

    def setup_database(self):
        if self.force_recreate_db:
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
                            print(f"Executed: {query_single_line[:50]}...")
                        except Exception as e:
                            print(f"------> Failed to execute query: {e}")

    def get_session(self):
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        return SessionLocal()

    def fetch_data_from_db(self, query: str):
        with self.get_session() as session:
            result = session.execute(text(query)).fetchall()
            return [row for row in result]

    def delete_table_if_exists(self, table_name: str):
        with self.engine.connect() as conn:
            try:
                conn.execute(text(f"DROP TABLE IF EXISTS {table_name};"))
                print(f"Table '{table_name}' deleted successfully.")
            except Exception as e:
                print(f"Failed to delete table: {e}")



# Example Usage
if __name__ == "__main__":
    mysql_interface = DatabaseInterface(db_type='tidb', db_name='test_creation', force_recreate_db=True)
    mysql_interface.setup_database()
    mysql_interface.create_tables("database/schemas.sql")
