import os
from dotenv import load_dotenv
load_dotenv()  # This will load the variables from the .env file

from lamatidb.interfaces.settings_manager import SettingsManager
from lamatidb.interfaces.index_interface import IndexInterface
from lamatidb.interfaces.query_interface import QueryInterface, FilterCondition
from typing import List

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

"""question_gen = OpenAIQuestionGenerator.from_defaults(llm=llm)
question_gen.get_prompts()"""


# Example 1: Granular Retrieval and Synthesis (Similarity Search)
"""query_interface.configure_retriever(similarity_top_k=100)
query_interface.configure_response_synthesizer()
query_interface.assemble_query_engine()
response = query_interface.perform_query("Neurological and cerebral conditions.")
query_interface.inspect_similarity_scores(response.source_nodes)"""

# Example 1.1: More clean for simple semantic search, without synthesiser
"""query_interface.configure_retriever(similarity_top_k=200)
source_nodes = query_interface.retriever.retrieve("List all documents.")
query_interface.inspect_similarity_scores(source_nodes)"""

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


# ==================================================
# Summary
# ==================================================

import mysql.connector
import os

# Database and vector table names
DB_NAME = os.environ['TIDB_DB_NAME']
VECTOR_TABLE_NAME = "scibert_alldata"
# Load or create the index
index_interface = IndexInterface(DB_NAME, VECTOR_TABLE_NAME)
index_interface.load_index_from_vector_store()
index = index_interface.get_index()


def get_db_connection():
    connection = mysql.connector.connect(
        host=os.getenv('TIDB_HOST'),
        user=os.getenv('TIDB_USERNAME'),
        password=os.getenv('TIDB_PASSWORD'),
        database=DB_NAME
    )
    return connection

cursor = get_db_connection().cursor(dictionary=True)

# View the table structure
def show_table_structure(table_name):
    cursor.execute(f"DESCRIBE {table_name}")
    schema = cursor.fetchall()
    print("Table Structure:")
    for column in schema:
        print(column)

def summarize_documents_by_ids(
        #db: Session,
        document_ids: List[str],
        index: QueryInterface, 
        ) -> str:
    """
    Summarizes the combined content of multiple documents identified by their IDs.
    """
    filters = [
        {
            "key": "source", # source or source_id ?
            "value": doc_id,
            "operator": "==",
        } for doc_id in document_ids
    ]

    # Initialize and configure QueryInterface
    sum_query_interface = QueryInterface(index)
    sum_query_interface.configure_retriever(similarity_top_k=1000, metadata_filters=filters, condition=FilterCondition.OR) # removed for testing for now: , metadata_filters=filters
    sum_query_interface.configure_response_synthesizer()
    sum_query_interface.assemble_query_engine()
        
    prompt = f"""You are a skilled researcher and summarization expert. Your task is to summarize the academic articles based on their abstracts into one cohesive description. Each article may come from a different field or focus on different aspects (theory, experiments, reviews, etc.), so ensure your summary reflects the key points accurately for each one.  
    Form a cohesive paragraph that explains what the abstracts are generally about. Ensure you encapsulate the following topics from each of the abstracts:
    1. Discipline or Topic: Identify the general areas of exploration for each abstract, if many overlap just include the overlapping topic once
    2. Objective or Focus: Describe the main question, objective, or hypothesis the articles.
    3. Methodology or Approach: Mention the type of study (e.g., experiment, survey, case study, literature review) and any notable techniques used.
    Be concise but thorough, extracting only the most important information from the abstracts. Do not list each article one at a time but rather refer to the general idea of all articles. Keep your summary to a maximum of 75 words."""

    response = sum_query_interface.perform_query(prompt)
    return response

ids = ["16625992","16625812","16625969","16625681"]
print(summarize_documents_by_ids(document_ids=ids, index=index))