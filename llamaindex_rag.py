
import streamlit as st
from backend.lamatidb.interfaces.index_interface import IndexInterface
from backend.lamatidb.interfaces.query_interface import QueryInterface

CHAT_WITH_DATA_DB = "test"
CHAT_WITH_DATA_VECTOR_TABLE_NAME = "Ben_full_docs_v2"


cwd_index_interface = IndexInterface(CHAT_WITH_DATA_DB,CHAT_WITH_DATA_VECTOR_TABLE_NAME)
cwd_index_interface.load_index_from_vector_store()
cwd_index = cwd_index_interface.get_index()

def chat_with_documents(query):
    query_interface = QueryInterface(cwd_index)
    query_interface.configure_retriever(similarity_top_k=100)
    query_interface.configure_response_synthesizer()
    query_interface.assemble_query_engine()
    response = query_interface.perform_query(query)
    return str(response)


if "messages" not in st.session_state:
    st.session_state.messages = []

messageHistoryContainer = st.container()
inputContainer = st.container()

with inputContainer:
    if(prompt := st.chat_input("Ask a question about the papers")):
        st.session_state.messages.append({"role":"user","content":prompt})
        response = chat_with_documents(prompt)
        st.session_state.messages.append({"role":"assistant","content":response})
with messageHistoryContainer:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
