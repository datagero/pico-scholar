import os
import uuid
import hashlib
import base64
import pandas as pd
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from lamatidb.interfaces.database_interfaces.mysql_interface import MySQLInterface
from lamatidb.interfaces.database_interfaces.database_interface import DatabaseInterface
from lamatidb.interfaces.metadata_interface import Metadata
from sqlalchemy import text

def generate_short_uuid():
    # Generate a UUID4 and take the first 16 characters as a hexadecimal number
    uuid_str = uuid.uuid4().int
    short_uuid = str(uuid_str)[:12]  # Take the first 12 digits of the numeric UUID
    return short_uuid

def generate_hash_key(input_str, length=16):
    """
    Generate a short numeric hash key.

    Parameters:
    input_str (str): The input string to hash (e.g., concatenation of documentId and databaseId).
    length (int): The desired length of the resulting hash key.

    Returns:
    str: A numeric hash key of the specified length.
    """
    # Generate a SHA-256 hash of the input string
    sha256_hash = hashlib.sha256(input_str.encode()).digest()
    
    # Convert the hash to a Base64 encoded string, then remove non-numeric characters
    base64_hash = base64.urlsafe_b64encode(sha256_hash).decode('utf-8').rstrip('=')
    numeric_hash = ''.join(filter(str.isdigit, base64_hash))
    
    # Trim or pad the numeric hash to the desired length
    if len(numeric_hash) > length:
        numeric_hash = numeric_hash[:length]
    else:
        numeric_hash = numeric_hash.ljust(length, '0')  # Pad with zeros if too short
    
    return numeric_hash

class Ingestor:
    def __init__(self, db_type, db_name):
        self.mysql_interface = DatabaseInterface(db_type=db_type, db_name=db_name)
        # self.mysql_interface = MySQLInterface()
        self.mysql_interface.setup_database()
        self.engine = self.mysql_interface.engine
        self.metadata_processor = Metadata()  # Initialize the Metadata class

    def insert_data(self, session: Session, table_name: str, data: pd.DataFrame):
        try:
            data.to_sql(table_name, con=session.bind, if_exists='append', index=False)
            print(f"Data inserted into {table_name} successfully, {len(data)} records.")
        except IntegrityError as e:
            print(f"Data insertion failed: {e}")

    def process_csv(self, csv_file: str):
        raise NotImplementedError("Subclasses should implement this method.")

    def ensure_database_exists(self, database_name, description=None):
        """
        Ensure that the logical document database exists in the AcademicDatabases table. 
        If it doesn't exist, prompt the user for a description and create it.
        """
        with self.mysql_interface.get_session() as session:
            query = "SELECT databaseId FROM `AcademicDatabases` WHERE databaseName = :database_name"
            result = session.execute(text(query), {"database_name": database_name}).fetchone()

            if result:
                database_id = result[0]
                print(f"Academic Database '{database_name}' found with ID '{database_id}'.")
            else:
                # Prompt for a description if the database doesn't exist
                database_id = generate_short_uuid()
                if not description:
                    description = input(f"Enter a description for the new database '{database_name}': ")
                insert_query = """
                    INSERT INTO `AcademicDatabases` (databaseId, databaseName, description) 
                    VALUES (:database_id, :database_name, :description)
                """
                session.execute(text(insert_query), {"database_id": database_id, "database_name": database_name, "description": description})
                session.commit()
                database_id = session.execute(text(query), {"database_name": database_name}).fetchone()[0]
                print(f"Database '{database_name}' created with ID '{database_id}'.")
        return database_id

    def get_mapping_if_not_exists(self, session: Session, database_id: str, document_id: str):
        """
        Insert the document-to-database mapping only if it does not already exist.
        
        :param session: SQLAlchemy session object.
        :param document_id: The ID of the document to map.
        """
        document_id_str = str(document_id)
        database_id_str = str(database_id)

        hash_key = generate_hash_key(pd.Series([document_id_str + database_id_str]).values[0])
        query = """
            SELECT 1 FROM `DocumentDatabaseMapping` WHERE documentId = :document_id AND databaseId = :database_id
        """
        result = session.execute(text(query), {"document_id": document_id, "database_id": self.database_id}).fetchone()

        if not result:
            document_mapping = {
                'documentId': document_id,
                'databaseId': database_id,
                'hashKey': hash_key
            }
            return document_mapping
        else:
            print(f"Mapping for document '{document_id}' in database '{database_id}' already exists.")

# Example subclass for abstract ingestion
class AbstractIngestor(Ingestor):

    def __init__(self, db_type='tidb', db_name='test_creation'):
        super().__init__(db_type=db_type, db_name=db_name)
        self.database_id = None

    def process_csv(self, csv_file: str, database_description=None):

        database_name = os.path.basename(os.path.dirname(csv_file))
        self.database_id = self.ensure_database_exists(database_name, description=database_description)

        df = pd.read_csv(csv_file)

        # Process and insert data into the Document table
        document_data = df[['PMID', 'Title', 'Authors', 'Publication Year']].copy()
        document_data.columns = ['documentId', 'title', 'author', 'year']

        # Process and insert data into the DocumentAbstract table
        document_abstract_data = df[['PMID', 'Abstract']].copy()
        document_abstract_data.columns = ['documentId', 'abstract']

        # Insert data into the corresponding tables
        with self.mysql_interface.get_session() as session:
            self.insert_data(session, 'Document', document_data)
            self.insert_data(session, 'DocumentAbstract', document_abstract_data)

            # Accumulate mappings and add new ones to database
            mappings_to_add = [self.get_mapping_if_not_exists(session, self.database_id, str(x)) 
                            for x in document_data['documentId']]
            # Remove None values from the list
            mappings_to_add = [x for x in mappings_to_add if x]

            # Convert the list of dictionaries to a DataFrame
            mappings_df = pd.DataFrame(mappings_to_add)

            if not mappings_df.empty:
                self.insert_data(session, 'DocumentDatabaseMapping', mappings_df)
                

        # After processing CSV, process PICO metadata
        self.process_pico_metadata(csv_file)

    def process_pico_metadata(self, df: pd.DataFrame, local_llm:bool=False):

        # Process each abstract to extract PICO metadata
        bulk_insert_data = {'raw': [], 'enhanced': []}

        # Process each abstract to extract PICO metadata
        for _, row in df.iterrows():
            document_id = str(row['documentId'])
            abstract_text = row['abstract']

            # Skip if no text to process
            if not abstract_text or pd.isnull(abstract_text):
                continue

            # Process the abstract using the metadata processor
            processed_terms, enhanced_terms = self.metadata_processor.process_text([abstract_text], local_llm=local_llm)

            terms_dict = {'raw': processed_terms, 'enhanced': enhanced_terms}

            for label, terms in terms_dict.items():
                for term in terms:
                    term.update({'documentId': document_id})
                    bulk_insert_data[label].append(term)

        # Convert lists to DataFrames and perform bulk insert
        with self.mysql_interface.get_session() as session:
            for label, data in bulk_insert_data.items():
                if data:  # Ensure there is data to insert
                    pico_df = pd.DataFrame(data)

                    # Get duplicated document ids
                    # duplicated_ids = pico_df[pico_df.duplicated(subset='documentId')]['documentId'].unique()

                    self.insert_data(session, f'DocumentPICO_{label}', pico_df)

    def fetch_unprocessed_pico_data(self):
        """
        Fetch PMIDs and abstracts that are not yet processed into the DocumentPICO_ tables.
        
        :param session: SQLAlchemy session object.
        :return: DataFrame containing unprocessed PMIDs and their abstracts.
        """
        # Query to find PMIDs not in DocumentPICO_raw (assuming the same PMIDs would be in all DocumentPICO_ tables)
        query = """
            SELECT da.documentId, da.abstract
            FROM DocumentAbstract da
            LEFT JOIN DocumentPICO_raw dp ON da.documentId = dp.documentId
            WHERE dp.documentId IS NULL
        """
        
        # Execute the query and fetch the results
        with self.mysql_interface.get_session() as session:
            result = session.execute(text(query)).fetchall()
        unprocessed_data = pd.DataFrame(result, columns=['documentId', 'abstract'])
        return unprocessed_data


# Example subclass for full document ingestion
class FullDocumentIngestor(Ingestor):

    def __init__(self, db_type='tidb', db_name='test_creation'):
        super().__init__(db_type=db_type, db_name=db_name)
        self.database_id = None

    def get_docID(self, pmid):
        # returns pcmid
        return

    def process_blob(self, pdf_path: str, document_id: str):
        database_name = os.path.basename(os.path.dirname(pdf_path))
        self.database_id = self.ensure_database_exists(database_name)

        # Read the PDF binary data
        with open(pdf_path, 'rb') as file:
            blob_data = file.read()

        # Create a DataFrame for inserting into the DocumentFull table
        document_full_data = pd.DataFrame({
            'documentId': [document_id],
            'pdfBlob': [blob_data]
        })

        # Insert the data into the DocumentFull table
        with self.mysql_interface.get_session() as session:
            self.insert_data(session, 'DocumentFull', document_full_data)

            # Insert mapping if it doesn't exist
            mappings_to_add = self.get_mapping_if_not_exists(session, self.database_id, str(document_id))
            if mappings_to_add :
                self.insert_data(session, 'DocumentDatabaseMapping', mappings_to_add)

if __name__ == "__main__":
    # Example for Abstract Ingestion
    abstract_csv_file = 'datalake/mock_data/abstracts.csv'

    abstract_ingestor = AbstractIngestor()
    abstract_ingestor.process_csv(abstract_csv_file, database_description="Mock Abstracts Database")

    # Example for Full Document Ingestion
    full_document_pdf_file = 'datalake/mock_data/16625675.pdf'
    
    full_document_ingestor = FullDocumentIngestor()
    full_document_ingestor.process_blob(full_document_pdf_file, '16625675')
