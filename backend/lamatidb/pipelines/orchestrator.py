import os
from dotenv import load_dotenv
load_dotenv()  # This will load the variables from the .env file

from lamatidb.interfaces.index_interface import IndexInterface
from lamatidb.interfaces.database_interfaces.tidb_interface import TiDBInterface
from lamatidb.interfaces.settings_manager import SettingsManager

from lamatidb.interfaces.database_interfaces.database_interface import DatabaseInterface
from lamatidb.interfaces.mysql_ingestors.abstract_ingestor import AbstractIngestor, FullDocumentIngestor
from lamatidb.interfaces.tidb_loaders.vector_loader_interface import LoaderPubMedAbstracts, LoaderPubMedPICO, LoaderPubMedFullText

# Set global settings
SettingsManager.set_global_settings(set_local=False)

vector_table_options = ["scibert_alldata","scibert_smalldata","mocked_data"]

# Database and vector table names
DB_NAME = os.environ['TIDB_DB_NAME']
VECTOR_TABLE_NAME = vector_table_options[0]

# # Create the database if it doesn't exist
# tidb_interface = TiDBInterface(DB_NAME)
# tidb_interface.create_db_if_not_exists() # Uncomment if you need to create the database
# tidb_interface.delete_table(VECTOR_TABLE_NAME)  # Uncomment if you need to delete the table

# # Delete vectors that do not have PICO metadata
# tidb_interface = TiDBInterface(DB_NAME, VECTOR_TABLE_NAME)
# tidb_interface.delete_entries_missing_metadata(required_metadata_keys=['pico_p', 'pico_i', 'pico_c', 'pico_o'])


# ==============================================================================================
#           Optional - Ingest your data (only if needed to load data/create index)
#           ----------------------------------------------------------------------

datastore_db = os.environ['DATASTORE_HOST']
datastore_db_name = os.environ['MYSQL_DB_NAME']

# # Delete all existing tables
# # mysql_interface = DatabaseInterface(db_type='mysql', db_name='test_creation', force_recreate_db=True)
# mysql_interface = DatabaseInterface(db_type=datastore_db, db_name=datastore_db_name, force_recreate_db=True)
# mysql_interface.setup_database()
# mysql_interface.create_tables("database/schemas.sql")

# # # abstract_csv_file = 'datalake/mock_data/abstracts2.csv'
abstract_csv_file = 'datalake/pubmed/pubmed24n0541.csv'
# abstract_ingestor = AbstractIngestor(db_type=datastore_db, db_name=datastore_db_name)
# abstract_ingestor.process_csv(abstract_csv_file, enhanced_pico=False, database_description="Sampled PubMed datasets for abstracts and fulltext")

# # Recovery of PICO Data into the database
# abstract_ingestor = AbstractIngestor(db_type=datastore_db, db_name=datastore_db_name)
# abstract_ingestor.recovery_load_pico_enhanced('datalake/pubmed/recovered_pico_data.json')

# # Load data from MySQL and process it into LlamaIndex documents
# loader = LoaderPubMedAbstracts(db_type=datastore_db, db_name=datastore_db_name)
# loader.load_data()
# loader.process_data()

# # Retrieve the documents and feed into LlamaIndex
# documents = loader.get_documents()
# index_interface = IndexInterface(DB_NAME, VECTOR_TABLE_NAME)
# index_interface.create_index(documents=documents) # Uncomment only if need to create / append to index
# ==============================================================================================
# ==============================================================================================
#                   Optional - Ingest your Full Document data 
#                   (only if needed to load data/create index)
#           ----------------------------------------------------------------------

# abstract_csv_file = 'datalake/pubmed/pubmed24n0541.csv'
# mapping_id_file = 'datalake/pubmed/PMC-ids-small.csv'
# fulltext_ingestor = FullDocumentIngestor(mapping_file=mapping_id_file, db_type=datastore_db, db_name=datastore_db_name)
# fulltext_ingestor.process_csv(abstract_csv_file, limitIDs=True, database_description="Mock Abstracts Database")

# # # Load data from MySQL and process it into LlamaIndex documents
# loader = LoaderPubMedFullText(db_type=datastore_db, db_name=datastore_db_name)
# loader.load_data()
# loader.process_data()

# documents = loader.get_documents()
# index_interface = IndexInterface(DB_NAME, VECTOR_TABLE_NAME+"_fulltext")
# index_interface.create_index(documents=documents) # Uncomment only if need to create / append to index

# ==============================================================================================


# # Adhoc generate PICOs and upsert to tables and vector databases
abstract_ingestor = AbstractIngestor(db_type=datastore_db, db_name=datastore_db_name)
# unprocessed_data = abstract_ingestor.fetch_unprocessed_pico_data()
abstract_ingestor.process_pico_metadata(abstract_csv_file, local_llm=False)

# loader = LoaderPubMedAbstracts(db_type=datastore_db, db_name=datastore_db_name)
# loader.load_data()
# # Then we'd need to re-create/add to the index/VectorDB for the unprocessed_data

# # ==============================================================================================
# # Create PICO/Metadata Indexes - it is 15 combinations so it may take 10-20mins
# # Load data from MySQL and process it into LlamaIndex documents
# loader = LoaderPubMedPICO(db_type=datastore_db, db_name=datastore_db_name)
# loader.load_data()
# loader.process_data()

# # Retrieve the documents and feed into LlamaIndex
# documents_dict = loader.get_documents_dict()

# for key, documents in documents_dict.items():
#     index_interface = IndexInterface(DB_NAME, VECTOR_TABLE_NAME+"_"+key)
#     index_interface.create_index(documents=documents) # Uncomment only if need to create / append to index


# # Test Load a PICO Index
# index_interface = IndexInterface(DB_NAME, VECTOR_TABLE_NAME+"_p")
# index_interface.load_index_from_vector_store()
# index = index_interface.get_index()

# # Mock Similarity Search Results
# from lamatidb.interfaces.query_interface import QueryInterface
# query_interface = QueryInterface(index)
# query_interface.configure_retriever(similarity_top_k=100)
# source_nodes = query_interface.retriever.retrieve("children with Diabetes mellitus")
# query_interface.inspect_similarity_scores(source_nodes)

# ==============================================================================================

################################################################################################

# Mock Similarity Search Results
from lamatidb.interfaces.query_interface import QueryInterface

# Load or create the index
index_interface = IndexInterface(DB_NAME, VECTOR_TABLE_NAME+"_fulltext")
index_interface.load_index_from_vector_store()
index = index_interface.get_index()


# Initialize the query interface with your index
query_interface = QueryInterface(index)

# # Example 1: Granular Retrieval and Synthesis (Similarity Search)
# query_interface.configure_retriever(similarity_top_k=100)
# query_interface.configure_response_synthesizer()
# query_interface.assemble_query_engine()
# response = query_interface.perform_query("Neurological and cerebral conditions.")
# query_interface.inspect_similarity_scores(response.source_nodes)

# Example 1.1: More clean for simple semantic search, without synthesiser
query_interface.configure_retriever(similarity_top_k=200)
source_nodes = query_interface.retriever.retrieve("List all documents.")
query_interface.inspect_similarity_scores(source_nodes)

# # Example 2: RAG-based Query Engine
# query_interface.build_rag_query_engine(similarity_top_k=100)
# # response = query_interface.perform_query("List all the titles of the books mentioned in the documents.")
# response = query_interface.perform_query("Neurological and cerebral conditions.")
# query_interface.inspect_similarity_scores(response.source_nodes)

# Example 3: Metadata Filtered Query
filters = [
    {"key": "source", "value": "16625676", "operator": "=="},
    # Add more filters as needed
]

# Case 3.1 Just Retrieval
query_interface.configure_retriever(similarity_top_k=100, metadata_filters=filters)
source_nodes = query_interface.retriever.retrieve("Neurological and cerebral conditions.")

# Case 3.2 With Syntesiser (By Default - requires LLM with metadata/context_window/etc...)
response = query_interface.perform_metadata_filtered_query("What is the specific focus of the documents?", filters)
print(response)

# # Example 4: Generate PICO Summary
# pico_metadata = {'I-INT': ['one intervention'], 'I-PAR': ['school kids', 'young'], 'I-OUT': ['It worked!']}

# pico_query = ("""For the given PICO Extraction (Patient, Intervention, Outcome): '{pico_metadata}' look at the source abstract and give
#               me a short sentence that accurately represents PICO for the document. You should return a dictionary
#               with {'I-INT': [Generated Sentence Related to Intervention], 'I-PAR': [Generated Sentence Related to
#               study Participant], 'I-OUT': [Generated Sentence Related to study Outputs]}""")
# response = query_interface.generate_pico_summary("16625676", pico_query)

# {'I-INT': 'This study focused only on one intervention, not taking into consideration the rest', 'I-PAR': 'Studies 33 school kids', 'I-OUT': 'The study results are...'}

# print(response)
