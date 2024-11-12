import pandas as pd
from lamatidb.interfaces.ingestion_interfaces.pubmed_handler import PubMedHandler

MAX_METADATA_LENGTH = 1024
MAX_AUTHORS = 5

def get_last_part(pmid):
    if isinstance(pmid, str):  # Check if pmid is a string
        parts = pmid.split('/')
        return parts[-1] if parts else pmid  # Return last part if available
    return pmid  # Return as is if not a string (e.g., NaN)

# Define the utility functions
def find_large_metadata_records(documents, max_length=MAX_METADATA_LENGTH):
    """
    Identify records with metadata exceeding the specified length.
    """
    large_metadata_records = []
    
    for doc in documents:
        metadata_length = len(str(doc.metadata)) if doc.metadata else 0
        if metadata_length > max_length:
            large_metadata_records.append(doc)
    
    return large_metadata_records

def reduce_authors_in_metadata(metadata, max_authors=MAX_AUTHORS):
    """
    Reduce the author list in metadata to a specified number and add 'et al.' if shortened.
    
    Parameters:
        metadata (dict): Metadata of a document containing an 'authors' key with a comma-separated string of authors.
        max_authors (int): Maximum number of authors to keep.
        
    Returns:
        dict: Updated metadata with a reduced author list.
    """
    if 'authors' in metadata and isinstance(metadata['authors'], str):
        authors_list = [author.strip() for author in metadata['authors'].split(',')]  # Split and strip each author
        if len(authors_list) > max_authors:
            # Keep only the first max_authors and add 'et al.'
            metadata['authors'] = ', '.join(authors_list[:max_authors]) + ', et al.'
        else:
            metadata['authors'] = ', '.join(authors_list)  # Rejoin without "et al." if within limit
    return metadata


def clean_dataframe_prioritize_included(df, id_column="pmid_clean", label_column="label_included"):
    """
    Cleans the DataFrame by removing rows with null values in the ID column, 
    then removing duplicate rows based on the specified ID column, 
    prioritizing rows where the label column has a value of 1 (indicating inclusion).
    
    Parameters:
    - df (pd.DataFrame): The DataFrame containing the data.
    - id_column (str): The column name for unique IDs (e.g., 'pmid_clean').
    - label_column (str): The column indicating inclusion (1) or exclusion (0).
    
    Returns:
    - pd.DataFrame: A cleaned DataFrame with nulls excluded, duplicates removed, and 'included' labels prioritized.
    """
    # Step 1: Remove rows where `pmid_clean` is null
    df_non_null = df[df[id_column].notna()].copy()
    
    # Step 2: Sort the DataFrame so rows with `label_included == 1` come before `0`
    sorted_df = df_non_null.sort_values(by=label_column, ascending=False)
    
    # Step 3: Drop duplicates based on the ID column, keeping the first occurrence
    # (the first occurrence will have `label_included == 1` if it exists for that ID)
    cleaned_df = sorted_df.drop_duplicates(subset=id_column, keep="first").reset_index(drop=True)
    
    return cleaned_df

if __name__ == "__main__":
    # Example usage
    study_name = 'Menon_2022'
    synergy_data_path = f"datalake/synergy/{study_name}_ids.csv"
    synergy_df = pd.read_csv(synergy_data_path)

    # Get pmids from the synergy data
    pmids = synergy_df["pmid"].apply(get_last_part).tolist()
    synergy_df["pmid_clean"] = pmids

    # Only keep the ones with valid pmids
    synergy_df_clean = clean_dataframe_prioritize_included(synergy_df)

    pub = PubMedHandler()

    # Now batch it in 10
    pubmed_data = []
    batch_size = 10
    for i in range(0, len(synergy_df_clean), batch_size):
        batch = synergy_df_clean.iloc[i:i + batch_size]
        batch_data = pub.fetch_pubmed_data_entrez(batch['pmid_clean'].tolist())
        pubmed_data.extend(batch_data)

    pmid_to_included = synergy_df_clean.set_index("pmid_clean")["label_included"].to_dict()

    # Add additional metadata
    for item in pubmed_data:
        item['study_name'] = study_name
        item['included_in_study'] = pmid_to_included[item['PMID']]

    # Save as CSV
    pubmed_df = pd.DataFrame(pubmed_data)
    pubmed_df.to_csv(f"datalake/synergy/processed_{study_name}_pubmed.csv", index=False)

# ==============================================================================================
    # Now, we want to load the CSV through our ingestor.
    # This will create documents in our local mysql database
    import os
    from lamatidb.interfaces.database_interfaces.database_interface import DatabaseInterface
    from lamatidb.interfaces.mysql_ingestors.abstract_ingestor import AbstractIngestor
    from dotenv import load_dotenv
    load_dotenv()  # This will load the variables from the .env file

    datastore_db = os.environ['DATASTORE_HOST']
    datastore_db_name = os.environ['MYSQL_DB_NAME']

    # ## Create the tables if they don't exist
    ## Delete all existing tables
    mysql_interface = DatabaseInterface(db_type=datastore_db, db_name=datastore_db_name, force_recreate_db=True)
    mysql_interface.setup_database()
    mysql_interface.create_tables("database/schemas.sql")

    abstract_csv_file = f'datalake/synergy/processed_{study_name}_pubmed.csv'
    abstract_ingestor = AbstractIngestor(db_type=datastore_db, db_name=datastore_db_name)
    abstract_ingestor.process_csv(abstract_csv_file, enhanced_pico=False, database_description="Sampled data from Synergy datasets for labelled included and excluded PMIDs from systematic review")

# ==============================================================================================
    # Now that the data is loaded into the database, we can load it into the LlamaIndex
    import os
    from lamatidb.interfaces.tidb_loaders.vector_loader_interface import LoaderPubMedAbstracts
    from lamatidb.interfaces.index_interface import IndexInterface
    from dotenv import load_dotenv
    load_dotenv()  # This will load the variables from the .env file

    # Set global settings -- important to use the correct embedding model
    from lamatidb.interfaces.settings_manager import SettingsManager
    SettingsManager.set_global_settings(set_local=False)

    # Database and vector table names
    DB_NAME = os.environ['TIDB_DB_NAME']
    VECTOR_TABLE_NAME = "scibert_synergy"

    datastore_db = os.environ['DATASTORE_HOST']
    datastore_db_name = os.environ['MYSQL_DB_NAME']

    # Load data from MySQL and process it into LlamaIndex documents
    loader = LoaderPubMedAbstracts(db_type=datastore_db, db_name=datastore_db_name)
    loader.load_data()
    loader.process_data()

    # Retrieve the documents and feed into LlamaIndex
    documents = loader.get_documents()
    large_metadata_records = find_large_metadata_records(documents, MAX_METADATA_LENGTH)
    
    # Modify documents with large metadata
    for doc in large_metadata_records:
        doc.metadata = reduce_authors_in_metadata(doc.metadata, MAX_AUTHORS)
    

    index_interface = IndexInterface(DB_NAME, VECTOR_TABLE_NAME)
    index_interface.create_index(documents=documents) # Uncomment only if need to create / append to index


from lamatidb.interfaces.index_interface import IndexInterface
from lamatidb.interfaces.query_interface import QueryInterface
from dotenv import load_dotenv
load_dotenv()  # This will load the variables from the .env file

datastore_db = os.environ['DATASTORE_HOST']
datastore_db_name = os.environ['MYSQL_DB_NAME']
# Test Load Index
index_interface = IndexInterface(DB_NAME, VECTOR_TABLE_NAME)
index_interface.load_index_from_vector_store()
index = index_interface.get_index()

# # Mock Similarity Search Results
query_interface = QueryInterface(index)
query_interface.configure_retriever(similarity_top_k=100)
source_nodes = query_interface.retriever.retrieve("Does D-penicillamine lead to higher treatment discontinuation than zinc or other therapies?")
query_interface.inspect_similarity_scores(source_nodes)



# ## Test Pubmed extraction:
#     pmids = ["26067812", "30049245"]  # List of PMIDs
#     pubmed_data = pub.fetch_pubmed_data_entrez(pmids)
#     for data in pubmed_data:
#         print(data)

