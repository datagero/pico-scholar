import os
import csv
from sqlalchemy import URL
from llama_index.core import StorageContext, VectorStoreIndex, Document
from llama_index.core.storage.index_store import SimpleIndexStore
from llama_index.vector_stores.tidbvector import TiDBVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import textwrap
import streamlit as st
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core import VectorStoreIndex, get_response_synthesizer

if "init" not in st.session_state:
    st.session_state.init = True
    st.session_state.tidb_connection_url = URL(
        "mysql+pymysql",
        username=os.environ['TIDB_USERNAME'],
        password=os.environ['TIDB_PASSWORD'],
        host=os.environ['TIDB_HOST'],
        port=4000,
        database="test_matias",
        query={"ssl_verify_cert": True, "ssl_verify_identity": True},
    )


# Define the TiDB Vector Store
    st.session_state.tidbvec = TiDBVectorStore(
        connection_string=st.session_state.tidb_connection_url,
        table_name= 'scibert_alldata',
        distance_strategy="cosine",
        vector_dimension=768, # SciBERT outputs 768-dimensional vectors
        drop_existing_table=False,
    )
    st.session_state.storage_context = StorageContext.from_defaults(vector_store=st.session_state.tidbvec)
    # TiDB automatically persists the embeddings when you use it as your vector store.


    st.session_state.embedding_model = HuggingFaceEmbedding(model_name="allenai/scibert_scivocab_uncased")
    st.session_state.index = VectorStoreIndex.from_vector_store(vector_store=st.session_state.tidbvec, embed_model=st.session_state.embedding_model)


    # configure retriever
    st.session_state.retriever = VectorIndexRetriever(
        index=st.session_state.index,
        similarity_top_k=100, #limit to top 100
    )

    # configure response synthesizer
    st.session_state.response_synthesizer = get_response_synthesizer()

    # assemble query engine
    st.session_state.query_engine = RetrieverQueryEngine(
        retriever=st.session_state.retriever,
        response_synthesizer=st.session_state.response_synthesizer,
        node_postprocessors=[SimilarityPostprocessor(similarity_cutoff=None)],
    )
if "messages" not in st.session_state:
    st.session_state.messages = []

messageHistoryContainer = st.container()
inputContainer = st.container()
with inputContainer:
    if(prompt := st.chat_input("Ask a question about the papers")):
        st.session_state.messages.append({"role":"user","content":prompt})
        response = st.session_state.query_engine.query(prompt)
        st.session_state.messages.append({"role":"assistant","content":str(response)})
with messageHistoryContainer:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
