import os
import uuid
import hashlib
import base64
import pandas as pd
import xml.etree.ElementTree as ET
import requests
import time
import pickle

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
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

    def process_csv(self, csv_file: str, database_description=None, enhanced_pico=False):

        database_name = os.path.basename(os.path.dirname(csv_file))
        self.database_id = self.ensure_database_exists(database_name, description=database_description)

        df = pd.read_csv(csv_file)

        # Drop if publication year is "unknown"
        df = df[df['Publication Year'] != 'Unknown']

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

            # Not active for DEMO - will only be loading pre-existing IDs
            # # Accumulate mappings and add new ones to database
            # mappings_to_add = [self.get_mapping_if_not_exists(session, self.database_id, str(x)) 
            #                 for x in document_data['documentId']]
            # # Remove None values from the list
            # mappings_to_add = [x for x in mappings_to_add if x]

            # # Convert the list of dictionaries to a DataFrame
            # mappings_df = pd.DataFrame(mappings_to_add)

            # if not mappings_df.empty:
            #     self.insert_data(session, 'DocumentDatabaseMapping', mappings_df)
                

        # After processing CSV, process PICO metadata
        self.process_pico_metadata(csv_file, enhanced_pico)

    def process_pico_metadata(self, csv_filepath:str, enhanced_pico:bool=False, local_llm:bool=False):

        df = pd.read_csv(csv_filepath)

        # Process and insert data into the Document table
        document_data = df[['PMID', 'Title', 'Authors', 'Abstract', 'Publication Year']].copy()
        document_data.columns = ['documentId', 'title', 'author', 'abstract', 'year']

        # Process each abstract to extract PICO metadata
        bulk_insert_data = {'raw': [], 'enhanced': []}

        # Process each abstract to extract PICO metadata
        for _, row in document_data.iterrows():
            document_id = str(row['documentId'])
            abstract_text = row['abstract']

            # Skip if no text to process
            if not abstract_text or pd.isnull(abstract_text):
                continue

            # Process the abstract using the metadata processor
            if enhanced_pico:
                processed_terms, enhanced_terms = self.metadata_processor.process_text([abstract_text], enhanced_pico=enhanced_pico, local_llm=local_llm)
                terms_dict = {'raw': processed_terms, 'enhanced': enhanced_terms}
            else:
                processed_terms, _ = self.metadata_processor.process_text([abstract_text], enhanced_pico=enhanced_pico, local_llm=local_llm)
                terms_dict = {'raw': processed_terms}

            for label, terms in terms_dict.items():
                for term in terms:
                    term.update({'documentId': document_id})
                    bulk_insert_data[label].append(term)

        # tmp functions to clean pico data so we can write it to datastore.
        def truncate_text(text, max_length):
            """
            Truncate the text to ensure it doesn't exceed the maximum length.
            """
            if isinstance(text, str) and len(text) > max_length:
                return text[:max_length]  # Truncate the text if it's too long
            return text

        def clean_non_scalar(row, column_lengths):
            """
            Cleans the row, converting lists to strings, ensuring scalar values, 
            and truncating text fields to fit within database limits.
            
            :param row: Row from the DataFrame.
            :param column_lengths: A dictionary specifying the maximum length for each column.
            """
            for col in row.index:
                max_length = column_lengths.get(col, 255)  # Default max length to 255 if not specified
                if isinstance(row[col], list):  # Convert list to string
                    row[col] = ', '.join(row[col]) if row[col] else None
                elif isinstance(row[col], str):  # Truncate text to fit column size
                    row[col] = truncate_text(row[col], max_length)
                elif pd.isnull(row[col]):  # Handle None/NaN
                    row[col] = None
            return row

        column_max_lengths = {
            'pico_p': 200,  # Truncate to 200 characters
            'pico_o': 200,  # Adjust as needed
            'pico_i': 200,  # Adjust as needed
            'pico_c': 200   # Adjust as needed, even though we set it to None initially
        }

        # Convert lists to DataFrames and perform bulk insert
        with self.mysql_interface.get_session() as session:
            for label, data in bulk_insert_data.items():
                if data:  # Ensure there is data to insert
                    pico_df = pd.DataFrame(data)
                    # Write null column
                    pico_df['pico_c'] = None
                    pico_df = pico_df.apply(clean_non_scalar, axis=1, args=(column_max_lengths,))
                    self.insert_data(session, f'DocumentPICO_{label}', pico_df)
    
    def recovery_load_pico_enhanced(self, json_filepath:str):
        # Load the JSON file into dataframe
        pico_df = pd.read_json(json_filepath)
        
        # Convert lists to DataFrames and perform bulk insert
        with self.mysql_interface.get_session() as session:
            self.insert_data(session, f'DocumentPICO_enhanced', pico_df)

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

    def __init__(self, mapping_file, db_type='tidb', db_name='test_creation'):
        super().__init__(db_type=db_type, db_name=db_name)
        self.database_id = None
        self.mapping_file = mapping_file
        self.mapping_df = None

    def get_docID_mapper(self, pmids: list, save_output=False):
        # Load the mapping file if not already loaded
        if self.mapping_df is None:
            if self.mapping_file:
                self.mapping_df = pd.read_csv(self.mapping_file, dtype={'PMID': str})
            else:
                # Note, this is a temporary solution to get the PMCIDs for the PMIDs
                # Will have to continue working on this for full functionality and UX

                # If there is no mapper file in lake, then create one through API calls
                if not os.path.exists('datalake/pubmed/pmcid_dict.pkl'):
                    pmcid_dict = self.pmid_to_pmcid_bulk(pmids)

                    # Persist dict and save it in lake
                    with open('datalake/pubmed/pmcid_dict.pkl', 'wb') as f:
                        pickle.dump(pmcid_dict, f)
                else:
                    with open('datalake/pubmed/pmcid_dict.pkl', 'rb') as f:
                        pmcid_dict = pickle.load(f)

        # Filter the DataFrame for the given PMIDs
        filtered_df = self.mapping_df[self.mapping_df['PMID'].isin(pmids)]

        # Create a dictionary where PMIDs are the keys and PMCIDs are the values
        doc_ids_dict = filtered_df.set_index('PMID')['PMCID'].to_dict()

        # Save small mapping file
        if save_output:
            parentpath = os.path.dirname(self.mapping_file)
            filtered_df.to_csv(f'{parentpath}/PMC-ids-small.csv', index=False)

        return doc_ids_dict

    def pmid_to_pmcid_bulk(self, pmids, tool_name="my_tool", email="my_email@example.com", batch_size=200):
        base_url = "https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/"
        pmcid_mapping = {}

        # Split PMIDs into batches
        for i in range(0, len(pmids), batch_size):
            batch_pmids = pmids[i:i + batch_size]
            ids_param = ",".join(batch_pmids)
            
            # Prepare the API request
            params = {
                "tool": tool_name,
                "email": email,
                "ids": ids_param,
                "format": "json"
            }
            
            # Make the API request
            response = requests.get(base_url, params=params)
            if response.status_code != 200:
                print(f"Failed to retrieve data for batch starting at index {i}. Status code: {response.status_code}")
                continue
            
            # Process the JSON response
            data = response.json()
            for record in data.get("records", []):
                pmid = record.get("pmid")
                pmcid = record.get("pmcid")
                if pmid and pmcid:
                    pmcid_mapping[pmid] = pmcid
            
            # Be respectful of the API rate limits
            time.sleep(1)  # Sleep 1 second between requests
        
        return pmcid_mapping

    def parse_and_clean_xml(self, xml_file_path: str) -> str:
        """
        Parse an XML file, extract text content, and clean it by removing excess newlines.

        Args:
            file_path (str): Path to the XML file.

        Returns:
            str: Cleaned text content extracted from the XML file.
        """
        tree = ET.parse(xml_file_path)
        root = tree.getroot()

        # Extract and clean text
        text_content = []
        for elem in root.iter():
            if elem.text:
                # Strip leading/trailing whitespace and replace multiple newlines with a single one
                cleaned_text = elem.text.strip().replace("\n", " ").replace("\r", " ")
                text_content.append(cleaned_text)

        # Join all cleaned text into a single string, ensuring consistent spacing
        return " ".join(text_content)

    def get_first_file_by_type(self, doc_directory_path: str, file_extension: str='.nxml') -> str:
        """
        Get the first file with a specific extension in a directory.

        Args:
            doc_directory_path (str): The directory to search in.
            file_extension (str): The file extension to filter by (e.g., '.xml').

        Returns:
            str: The path to the first matching file, or None if no match is found.
        """
        if file_extension == '.pdf':
            files = [file for file in os.listdir(doc_directory_path) if file.endswith(file_extension)]
            # Return the shortest PDF file (assuming it's the main document)
            file = min(files, key=len) if files else None
            return os.path.join(doc_directory_path, file)

        for file in os.listdir(doc_directory_path):
            if file.endswith(file_extension):
                return os.path.join(doc_directory_path, file)
        return None

    def download_full_document(self, ids:list, out_folder:str = 'pmc_data'):
        import requests
        import wget
        import tarfile
        from bs4 import BeautifulSoup
        import urllib.request

        if not os.path.exists(out_folder):
            os.makedirs(out_folder)

        for id in ids:
            response = requests.get(f'https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id={id}')
            soup = BeautifulSoup(response.content)
            if not soup.find('error'):
                link = soup.find('link')['href']

                # Handle FTP or HTTP/HTTPS download
                if link.startswith('ftp://'):
                    fname = os.path.join(out_folder, os.path.basename(link))
                    urllib.request.urlretrieve(link, fname)
                else:
                    fname = wget.download(link, out=out_folder)

                if fname.endswith("tar.gz"):
                    with tarfile.open(fname, "r:gz") as tar:
                        tar.extractall(path=out_folder)
                        tar.close()
                    os.remove(fname)

    def process_csv(self, csv_file: str, limitIDs:bool=False, download_fulldata=False, database_description=None):

        database_name = os.path.basename(os.path.dirname(csv_file))
        self.database_id = self.ensure_database_exists(database_name, description=database_description)

        df = pd.read_csv(csv_file)

        if limitIDs:
            # For DEMO, we limit our scope to preloaded PMCIDs (those that have PICO are in scope for the DEMO)
            query = "SELECT DISTINCT documentId FROM DocumentPICO_enhanced"
            results = self.mysql_interface.fetch_data_from_db(query)
            df = df[df['PMID'].astype(str).isin([x[0] for x in results])]

        # Process and insert data into the Document table
        document_data = df[['PMID', 'Title', 'Authors', 'Publication Year']].copy()
        document_data.columns = ['documentId', 'title', 'author', 'year']
        document_data['documentId'] = document_data['documentId'].astype(str)

        # Get PMCID using the PubMedHandler
        pmids = [str(x) for x in document_data['documentId'].tolist()]
        pmcid_dict = self.get_docID_mapper(pmids)

        if download_fulldata:
            document_data['PMCID'] = document_data['documentId'].map(pmcid_dict)

            # Get IDs that got PMCID
            ids = document_data[~document_data['PMCID'].isnull()]['PMCID'].tolist()
            print(f"Downloading {len(ids)} full documents (out of {len(document_data)} abstracts).")

            self.download_full_document(ids, out_folder='pmc_data')

        doc_paths = {pmcid: self.get_first_file_by_type(os.path.join('pmc_data', pmcid), '.pdf') for pmcid in os.listdir('pmc_data')}
        xml_paths = {pmcid: self.get_first_file_by_type(os.path.join('pmc_data', pmcid), '.nxml') for pmcid in os.listdir('pmc_data')}
        fulltext_dict = {pmcid: self.parse_and_clean_xml(path) for pmcid, path in xml_paths.items()}

        pmid_dict = {pmcid: pmid for pmid, pmcid in pmcid_dict.items()}
        for pmcid, doc_path in doc_paths.items():
            self.process_blob(doc_path, document_id=pmid_dict[pmcid], PMCID=pmcid, fulltext=fulltext_dict[pmcid])

        # ========================================================================================================
        # Some initial code to process the if is .nxml format
        # objects = {pmcid: self.parse_and_clean_xml(path) for pmcid, path in doc_paths.items()}
        # # Create a DataFrame for inserting into the DocumentFull table
        # pmid_dict = {pmcid: pmid for pmid, pmcid in pmcid_dict.items()}
        # document_full_data = pd.DataFrame(list(objects.items()), columns=['PMCID', 'pdfBlob'])
        # document_full_data['documentId'] = document_full_data['PMCID'].map(pmid_dict)

        # self.insert_df_to_db(document_full_data, document_id='PMCID')

    # def insert_df_to_db(self, df: pd.DataFrame, document_id: str):
    #     # Currently not in use and not tested -> This is dev for .nxml format
    #     # Insert the data into the DocumentFull table
    #     with self.mysql_interface.get_session() as session:
    #         self.insert_data(session, 'DocumentFull', df)

    #         # Insert mapping if it doesn't exist
    #         mappings_to_add = self.get_mapping_if_not_exists(session, self.database_id, str(document_id))
    #         if mappings_to_add :
    #             self.insert_data(session, 'DocumentDatabaseMapping', mappings_to_add)

    def process_blob(self, pdf_path: str, document_id: str, fulltext:str=None, PMCID: str = None):
        # Ignore the database_name for now -- This is more for PRD
        database_name = 'pubmed' #Default to pubmed for now
        self.database_id = self.ensure_database_exists(database_name)

        # Read the PDF binary data
        with open(pdf_path, 'rb') as file:
            blob_data = file.read()

        # Create a DataFrame for inserting into the DocumentFull table
        document_full_data = pd.DataFrame({
            'documentId': [document_id],
            'PMCID': [PMCID],
            'fullText': [fulltext],
            'pdfBlob': [blob_data]
        })

        # Insert the data into the DocumentFull table
        with self.mysql_interface.get_session() as session:
            self.insert_data(session, 'DocumentFull', document_full_data)

            # # IGNORE for now, as will only be loading pre-existing IDs Insert mapping if it doesn't exist
            # mappings_to_add = self.get_mapping_if_not_exists(session, self.database_id, str(document_id))
            # if mappings_to_add :
            #     self.insert_data(session, 'DocumentDatabaseMapping', mappings_to_add)

if __name__ == "__main__":
    # Example for Abstract Ingestion
    abstract_csv_file = 'datalake/mock_data/abstracts.csv'

    abstract_ingestor = AbstractIngestor()
    abstract_ingestor.process_csv(abstract_csv_file, database_description="Mock Abstracts Database")

    # Example for Full Document Ingestion
    full_document_pdf_file = 'datalake/mock_data/16625675.pdf'
    
    full_document_ingestor = FullDocumentIngestor()
    full_document_ingestor.process_blob(full_document_pdf_file, '16625675')
