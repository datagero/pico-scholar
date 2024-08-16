import os
from lamatidb.interfaces.loader_interface import LoaderPubMedCSV
from lamatidb.interfaces.index_interface import IndexInterface
from lamatidb.interfaces.tidb_interface import TiDBInterface
from lamatidb.interfaces.settings_manager import SettingsManager

# Set global settings
SettingsManager.set_global_settings()

# Database and vector table names
DB_NAME = os.environ['TIDB_DB_NAME']
# VECTOR_TABLE_NAME = "scibert_alldata"
VECTOR_TABLE_NAME = "scibert_alldata"

## Create the database if it doesn't exist
# tidb_interface = TiDBInterface(DB_NAME)
# tidb_interface.create_db_if_not_exists() # Uncomment if you need to create the database
# tidb_interface.delete_table(VECTOR_TABLE_NAME)  # Uncomment if you need to delete the table

# # Optional - Load your data (only if needed to load data/create index)
# csv_pubmed_path = 'pubmed_sample/pubmed24n0541.csv'
# data_loader = LoaderPubMedCSV(csv_pubmed_path)
# data_loader.load_data()
# data_loader.process_data()
# documents = data_loader.documents[:10]
# index_interface = IndexInterface(DB_NAME, VECTOR_TABLE_NAME)
# index_interface.create_index(documents=documents) # Uncomment only if need to create / append to index

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

# Example 4: Generate PICO Summary
pico_query = ("""For the given PICO Extraction (Patient, Intervention, Outcome) look at the source abstract and give
              me a short sentence that accurately represents PICO for the document. You should return a dictionary
              with {'I-INT': [Generated Sentence Related to Intervention], 'I-PAR': [Generated Sentence Related to
              study Participant], 'I-OUT': [Generated Sentence Related to study Outputs]}""")
response = query_interface.generate_pico_summary("16625676", pico_query)
print(response)
