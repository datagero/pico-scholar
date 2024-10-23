import os
from dotenv import load_dotenv
load_dotenv()  # This will load the variables from the .env file

from lamatidb.interfaces.settings_manager import SettingsManager
from lamatidb.interfaces.index_interface import IndexInterface
from lamatidb.interfaces.query_interface import QueryInterface

SettingsManager.set_global_settings(set_local=False)

vector_table_options = ["scibert_alldata","scibert_smalldata","mocked_data"]

# Database and vector table names
DB_NAME = os.environ['TIDB_DB_NAME']
VECTOR_TABLE_NAME = vector_table_options[0]
# Load or create the index
index_interface = IndexInterface(DB_NAME, VECTOR_TABLE_NAME+"_fulltext")
index_interface.load_index_from_vector_store()
index = index_interface.get_index()

# Initialize the query interface with your index
query_interface = QueryInterface(index)

# Example 1: Granular Retrieval and Synthesis (Similarity Search)
query_interface.configure_retriever(similarity_top_k=100)
query_interface.configure_response_synthesizer()
query_interface.assemble_query_engine()
response = query_interface.perform_query("Neurological and cerebral conditions.")
query_interface.inspect_similarity_scores(response.source_nodes)

# Example 1.1: More clean for simple semantic search, without synthesiser
query_interface.configure_retriever(similarity_top_k=200)
source_nodes = query_interface.retriever.retrieve("List all documents.")
query_interface.inspect_similarity_scores(source_nodes)

pass