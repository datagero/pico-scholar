import os
import json
from sqlalchemy import create_engine, text, URL
from sqlalchemy.orm import sessionmaker

class TiDBInterface:
    def __init__(self, db_name: str, vector_table_name: str=None):
        self.db_name = db_name
        self.vector_table_name = vector_table_name
        self.tidb_connection_url = URL(
            "mysql+pymysql",
            username=os.environ['TIDB_USERNAME'],
            password=os.environ['TIDB_PASSWORD'],
            host=os.environ['TIDB_HOST'],
            port=4000,
            database=self.db_name,
            query={"ssl_verify_cert": True, "ssl_verify_identity": True},
        )
        self.engine = None

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
        # SQL statement to create the database if it doesn't exist
        if not self.engine:
            self.engine = create_engine(self.tidb_connection_url)
        create_db_sql = f"DROP TABLE IF EXISTS {vector_table_name};"

        # Execute the SQL command
        with self.engine.connect() as connection:
            connection.execute(text(create_db_sql))

        print(f"Table '{vector_table_name}' deleted successfully (if it existed).")

    def get_session(self):
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        return SessionLocal()

    def retrieve_all_documents(self):
        """Retrieve all documents in the vector store along with their metadata."""
        query = f"SELECT id, meta FROM {self.vector_table_name}"

        with self.get_session() as session:
            result = session.execute(text(query)).fetchall()
            return [row for row in result]

    def delete_document_by_id(self, document_id):
        """Delete a specific document by its ID."""
        delete_query = f"DELETE FROM {self.vector_table_name} WHERE id = :doc_id"
        with self.engine.connect() as connection:
            connection.execute(text(delete_query), {'doc_id': document_id})

    def delete_entries_missing_metadata(self, required_metadata_keys):
        """
        Delete entries in the vector store that do not contain all required metadata keys.

        :param required_metadata_keys: List of metadata keys that must be present and non-null.
        """

        if not self.engine:
            self.engine = create_engine(self.tidb_connection_url)

        # Retrieve all documents in the vector store
        all_documents = self.retrieve_all_documents()

        # Filter out documents that are missing the required metadata
        documents_to_delete = []
        for doc_id, metadata_str in all_documents:
            # Parse the JSON metadata string
            metadata = json.loads(metadata_str)
            
            # Check if any of the required metadata keys are missing or have a null value
            if not all(metadata.get(key) is not None for key in required_metadata_keys):
                documents_to_delete.append(doc_id)

        # Perform bulk deletion if there are documents to delete
        if documents_to_delete:
            quoted_ids = ','.join(f"'{doc_id}'" for doc_id in documents_to_delete)
            delete_query = f"DELETE FROM {self.vector_table_name} WHERE id IN ({quoted_ids});"
            with self.engine.connect() as conn:
                a = conn.execute(text(delete_query))
                conn.commit()

            print(f"Deleted {len(documents_to_delete)} documents missing required metadata.")
        else:
            print("No documents to delete. All entries have the required metadata.")
