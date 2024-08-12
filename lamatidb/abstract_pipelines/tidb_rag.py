import os
import csv
from sqlalchemy import URL
from llama_index.core import StorageContext, VectorStoreIndex, Document
from llama_index.core.storage.index_store import SimpleIndexStore
from llama_index.vector_stores.tidbvector import TiDBVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

def read_csv(file_path):
    data = []
    with open(file_path, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            data.append(row)
    return data

# Load your data
file_path = 'pubmed_sample/pubmed24n0541.csv'
content = read_csv(file_path)


# # Sample data from your content
# # If abstract is empty, then fill it with title
# for row in content:
#     if row[3] == '':
#         row[3] = row[1]

# Actually, to get better quality results, let's ignore the records without abstract for now
# remove records without abstract
content = [x for x in content if x[3] != '']


sample_dict = {x[0]: {'text' : x[3], 'title': x[1], 'authors': x[2], 'year': x[4]} for x in content[1:][:100]}
sample_text = [x['text'] for x in sample_dict.values()]


# Load database and create index
embedding_model = HuggingFaceEmbedding(model_name="allenai/scibert_scivocab_uncased")


documents = [
    Document(
        text=values['text'],
        metadata={"source": doc_id,
                  "title": values['title'],
                  "authors": values['authors'],
                  "year": values['year']},
        # embedding=values['embedding'].tolist()  # Attach the precomputed embedding directly
    )
    for doc_id, values in sample_dict.items()
]

tidb_connection_url = URL(
    "mysql+pymysql",
    username=os.environ['TIDB_USERNAME'],
    password=os.environ['TIDB_PASSWORD'],
    host=os.environ['TIDB_HOST'],
    port=4000,
    database="test",
    query={"ssl_verify_cert": True, "ssl_verify_identity": True},
)


# Define the TiDB Vector Store
VECTOR_TABLE_NAME = "scibert_test4"
tidbvec = TiDBVectorStore(
    connection_string=tidb_connection_url,
    table_name=VECTOR_TABLE_NAME,
    distance_strategy="cosine",
    vector_dimension=768, # SciBERT outputs 768-dimensional vectors
    drop_existing_table=False,
)

# First Run: Create index
# Create the storage context and index
storage_context = StorageContext.from_defaults(vector_store=tidbvec)
# TiDB automatically persists the embeddings when you use it as your vector store.
index = VectorStoreIndex.from_documents(
    documents, 
    storage_context=storage_context, 
    embed_model=embedding_model,
    show_progress=True
)

# ### Currently cannot persist index, need to investigate further
# # # Persist index (ideally we want to persist into the database), check if there's native support 
# # like https://docs.llamaindex.ai/en/stable/module_guides/storing/index_stores/ or https://docs.llamaindex.ai/en/stable/api_reference/storage/index_store/simple/?h=simpleindexstore#llama_index.core.storage.index_store.SimpleIndexStore
# # storage_context.persist(persist_dir="pubmed_sample/lama_index")

# from llama_index.core import (
#     load_index_from_storage,
#     load_indices_from_storage,
#     load_graph_from_storage,
# )

# # Retrieve index from storage
# storage_context = StorageContext.from_defaults(vector_store=tidbvec, index_store=SimpleIndexStore.from_persist_dir(persist_dir="pubmed_sample/lama_index"))

# # don't need to specify index_id if there's only one index in storage context
# index = load_index_from_storage(storage_context)
# # indices = load_indices_from_storage(storage_context)  # loads all indices

# Example 1: Granular Retrieval and Synthesis
# Maybe we can use this as similarity/semantic search engine, but further experimentation is needed
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core import VectorStoreIndex, get_response_synthesizer

# configure retriever
retriever = VectorIndexRetriever(
    index=index,
    similarity_top_k=100, #limit to top 100
)

# configure response synthesizer
response_synthesizer = get_response_synthesizer()

# assemble query engine
query_engine = RetrieverQueryEngine(
    retriever=retriever,
    response_synthesizer=response_synthesizer,
    node_postprocessors=[SimilarityPostprocessor(similarity_cutoff=None)],
)

# query
# response = query_engine.query("List all the titles of the articles mentioned in the documents.")
response = query_engine.query("Neurological and cerebral conditions.")
print(response)


# Example of inspecting similarity scores (depending on your specific setup)
for node in response.source_nodes:
    source = node.metadata['source']
    title = node.metadata.get('title')
    abstract = node.text
    similarity = node.score
    print(f"Document {source} Title: {title}, Similarity: {similarity}")
    # print(f"Abstract: {abstract}")



# Example 2: Build RAG from Index
import textwrap

# Create a query engine based on the TiDB vector store
query_engine = index.as_query_engine(similarity_top_k=len(documents)*4)

# Example query
response = query_engine.query("what is isotherms?")
print(textwrap.fill(str(response), 100))


response = query_engine.query(
    "List all the titles of the books mentioned in the documents."
)
print(textwrap.fill(str(response), 100))



# You can also filter with metadata (if available)
from llama_index.core.vector_stores.types import (
    MetadataFilter,
    MetadataFilters,
)

# Example of filtering with metadata (adjust to your use case)
query_engine = index.as_query_engine(
    filters=MetadataFilters(
        filters=[
            MetadataFilter(key="source", value="16625676", operator="=="),
            # MetadataFilter(key="Patient", value="US Adults", operator="=="), # Practical example once we have PICO elements extracted...
        ]
    ),
    similarity_top_k=2,
)
response = query_engine.query("What is the specific focus of the documents?")
print(textwrap.fill(str(response), 100))

