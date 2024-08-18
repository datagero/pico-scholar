import os

from lamatidb.interfaces.index_interface import IndexInterface
from lamatidb.interfaces.tidb_interface import TiDBInterface
from lamatidb.interfaces.settings_manager import SettingsManager

from lamatidb.interfaces.mysql_interface import MySQLInterface
from lamatidb.interfaces.mysql_ingestors.abstract_ingestor import AbstractIngestor
from lamatidb.interfaces.tidb_loaders.vector_loader_interface import LoaderPubMedMySQL

# Set global settings
SettingsManager.set_global_settings()

vector_table_options = ["scibert_alldata","scibert_smalldata","mocked_data"]


# Database and vector table names
DB_NAME = os.environ['TIDB_DB_NAME']
VECTOR_TABLE_NAME = vector_table_options[2]

## Create the database if it doesn't exist
# tidb_interface = TiDBInterface(DB_NAME)
# tidb_interface.create_db_if_not_exists() # Uncomment if you need to create the database
# tidb_interface.delete_table(VECTOR_TABLE_NAME)  # Uncomment if you need to delete the table

# # ==============================================================================================
# #           Optional - Ingest your data (only if needed to load data/create index)
# #           ----------------------------------------------------------------------

# # Delete all existing tables
# mysql_interface = MySQLInterface(force_recreate_db=True)
# mysql_interface.setup_database()
# mysql_interface.create_tables("database/schemas.sql")

# abstract_csv_file = 'datalake/mock_data/abstracts2.csv'
# abstract_ingestor = AbstractIngestor()
# abstract_ingestor.process_csv(abstract_csv_file)

# # Load data from MySQL and process it into LlamaIndex documents
# loader = LoaderPubMedMySQL()
# loader.load_data()
# loader.process_data()

# # Retrieve the documents and feed into LlamaIndex
# documents = loader.get_documents()
# index_interface = IndexInterface(DB_NAME, VECTOR_TABLE_NAME)
# index_interface.create_index(documents=documents) # Uncomment only if need to create / append to index
# # ==============================================================================================


# Load or create the index
index_interface = IndexInterface(DB_NAME, VECTOR_TABLE_NAME)
index_interface.load_index_from_vector_store()
index = index_interface.get_index()


##############################################################################################

# Mock Similarity Search Results
from lamatidb.interfaces.query_interface import QueryInterface

# Initialize the query interface with your index
query_interface = QueryInterface(index)

# Example 1: Granular Retrieval and Synthesis (Similarity Search)
query_interface.configure_retriever(similarity_top_k=100)
query_interface.configure_response_synthesizer()
query_interface.assemble_query_engine()
response = query_interface.perform_query("Neurological and cerebral conditions.")
query_interface.inspect_similarity_scores(response.source_nodes)

# Example 1.1: More clean for simple semantic search, without synthesiser
query_interface.configure_retriever(similarity_top_k=100)
source_nodes = query_interface.retriever.retrieve("Neurological and cerebral conditions.")
query_interface.inspect_similarity_scores(source_nodes)

# Example 2: RAG-based Query Engine
query_interface.build_rag_query_engine(similarity_top_k=100)
# response = query_interface.perform_query("List all the titles of the books mentioned in the documents.")
response = query_interface.perform_query("Neurological and cerebral conditions.")
query_interface.inspect_similarity_scores(response.source_nodes)

# Example 3: Metadata Filtered Query
filters = [
    {"key": "source", "value": "16625676", "operator": "=="},
    # Add more filters as needed
]
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
