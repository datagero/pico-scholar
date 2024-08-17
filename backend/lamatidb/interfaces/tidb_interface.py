import os
from sqlalchemy import create_engine, text, URL

class TiDBInterface:
    def __init__(self, db_name: str):
        self.db_name = db_name

    def create_db_if_not_exists(self):
        # Define the TiDB Connection and Vector Store
        tidb_connection_url = URL(
            "mysql+pymysql",
            username=os.environ['TIDB_USERNAME'],
            password=os.environ['TIDB_PASSWORD'],
            host=os.environ['TIDB_HOST'],
            port=4000,
            database='mysql',
            query={"ssl_verify_cert": True, "ssl_verify_identity": True},
        )

        # SQL statement to create the database if it doesn't exist
        engine = create_engine(tidb_connection_url)
        create_db_sql = f"CREATE DATABASE IF NOT EXISTS {self.db_name};"

        # Execute the SQL command
        with engine.connect() as connection:
            connection.execute(text(create_db_sql))
        
        print(f"Database '{self.db_name}' created successfully (if not existed).")

    def delete_table_if_exists(self, vector_table_name: str):
        # Define the TiDB Connection and Vector Store
        tidb_connection_url = URL(
            "mysql+pymysql",
            username=os.environ['TIDB_USERNAME'],
            password=os.environ['TIDB_PASSWORD'],
            host=os.environ['TIDB_HOST'],
            port=4000,
            database=self.db_name,
            query={"ssl_verify_cert": True, "ssl_verify_identity": True},
        )

        # SQL statement to create the database if it doesn't exist
        engine = create_engine(tidb_connection_url)
        create_db_sql = f"DROP TABLE IF EXISTS {vector_table_name};"

        # Execute the SQL command
        with engine.connect() as connection:
            connection.execute(text(create_db_sql))

        print(f"Table '{vector_table_name}' deleted successfully (if it existed).")
