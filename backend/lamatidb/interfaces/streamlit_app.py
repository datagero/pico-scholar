# This is a placeholder code to assist with streamlit integration into our code

import streamlit as st
import os
# Set up orchestrator (maybe we move to different file)
from index_interface import IndexInterface
from settings_manager import SettingsManager
from query_interface import QueryInterface

# Set global settings
SettingsManager.set_global_settings()

# Database and vector table names
DB_NAME = "scibert_alldata_pico"
VECTOR_TABLE_NAME = 'scibert_alldata_fulltext'

index_interface_fulltext = IndexInterface(DB_NAME, VECTOR_TABLE_NAME+'_fulltext')
index_interface_fulltext.load_index_from_vector_store()
index_fulltext = index_interface_fulltext.get_index()

def chat_with_documents(query:str, PMID=None)->str:
    query_interface = QueryInterface(index_fulltext)
    query_interface.configure_retriever(similarity_top_k=100)
    query_interface.configure_response_synthesizer()
    query_interface.assemble_query_engine()

    if PMID is not None:
        filters = [
        {"key": "PMID", "value": str(PMID), "operator": "=="},
        ]
        response = query_interface.perform_metadata_filtered_query(query, filters)
        
    else:
        response = query_interface.perform_query(query)
    return str(response)

import streamlit as st


# Call the Streamlit run function with this module as the target
if __name__ == "__main__":

    if "init" not in st.session_state:
        st.session_state.init = True
        
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "pmid" not in st.session_state:
        current_directory = os.path.dirname(__file__)
        pmid_file_name = "pmid.txt"
        pmid_file_path = os.path.join(current_directory, pmid_file_name)
        with open(pmid_file_path, "r") as file:
            st.session_state.pmid =  str(file.read())

    messageHistoryContainer = st.container()
    inputContainer = st.container()
    with inputContainer:
        if(prompt := st.chat_input("Ask a question about the papers")):
            st.session_state.messages.append({"role":"user","content":prompt})
            response = chat_with_documents(prompt, st.session_state.pmid)
            st.session_state.messages.append({"role":"assistant","content":str(response)})
    with messageHistoryContainer:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])

