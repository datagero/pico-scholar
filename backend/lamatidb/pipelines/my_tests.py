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
index_interface = IndexInterface(DB_NAME, VECTOR_TABLE_NAME)
index_interface.load_index_from_vector_store()
index = index_interface.get_index()

# Initialize the query interface with your index
query_interface = QueryInterface(index)

from llama_index.core import PromptTemplate
from llama_index.llms.openai import OpenAI
llm = OpenAI(model="gpt-3.5-turbo")


#Query Rewriting (Custom)
query_gen_str = """\
You are a helpful assistant that generates multiple search queries based on a \
single input query. Generate {num_queries} search queries, one on each line, \
related to the following input query:
Query: {query}
Queries:
"""

query_gen_prompt = PromptTemplate(query_gen_str)

def generate_queries(query: str, llm, num_queries: int = 4):
    response = llm.predict(
        query_gen_prompt, num_queries=num_queries, query=query
    )
    # assume LLM proper put each query on a newline
    queries = response.split("\n")
    queries_str = "\n".join(queries)
    print(f"Generated queries:\n{queries_str}")
    return queries

queries = generate_queries("What happened at Interleaf and Viaweb?", llm)



# Query Rewriting (using QueryTransform)¶
from llama_index.core.indices.query.query_transform import HyDEQueryTransform
hyde = HyDEQueryTransform(include_original=True)
query_bundle = hyde.run("What is Bel?")


# Sub-Questions¶
from llama_index.core.question_gen import LLMQuestionGenerator
from llama_index.question_gen.openai import OpenAIQuestionGenerator

question_gen = OpenAIQuestionGenerator.from_defaults(llm=llm)
question_gen.get_prompts()


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

# ==================================================
# Linear Flow
# ==================================================


from sqlalchemy import create_engine, text, URL
from llama_index.core import StorageContext, VectorStoreIndex, Document
from llama_index.vector_stores.tidbvector import TiDBVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

TIDB_HOST='gateway01.us-east-1.prod.aws.tidbcloud.com'
TIDB_USERNAME='6K9ZXKTM8XD1n73.root'
TIDB_PASSWORD='sz0sT1mp4ZiMxmqQ'
TIDB_PORT=4000
TIDB_DB_NAME='scibert_alldata_pico'

vector_table_name = 'scibert_alldata'

DATABASE_URI = URL(
    "mysql+pymysql",
    username=TIDB_USERNAME,
    password=TIDB_PASSWORD,
    host=TIDB_HOST,
    port=TIDB_PORT,
    database=TIDB_DB_NAME,
    query={"ssl_verify_cert": True, "ssl_verify_identity": True},
)

tidbvec = TiDBVectorStore(
    connection_string=DATABASE_URI,
    table_name= vector_table_name,
    distance_strategy="cosine",
    vector_dimension=768, # SciBERT outputs 768-dimensional vectors
    drop_existing_table=False,
)

# engine = create_engine(DATABASE_URI, pool_size=10, max_overflow=20, pool_timeout=30, pool_recycle=1800)

embedding_model = HuggingFaceEmbedding(model_name="allenai/scibert_scivocab_uncased")

index = VectorStoreIndex.from_vector_store(
    vector_store=tidbvec,
    embed_model=embedding_model
)



