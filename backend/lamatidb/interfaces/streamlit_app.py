import streamlit as st

def init_query_interface():
    import os
    from dotenv import load_dotenv
    load_dotenv()  # This will load the variables from the .env file

    from backend.lamatidb.interfaces.index_interface import IndexInterface
    from backend.lamatidb.interfaces.settings_manager import SettingsManager
    from backend.lamatidb.interfaces.query_interface import QueryInterface

    # Set global settings
    SettingsManager.set_global_settings()

    # Database and vector table names
    DB_NAME = os.environ['TIDB_DB_NAME']
    VECTOR_TABLE_NAME = "scibert_alldata"

    # Load or create the index
    index_interface = IndexInterface(DB_NAME, VECTOR_TABLE_NAME)
    index_interface.load_index_from_vector_store()
    index = index_interface.get_index()

    # Initialize the QueryInterface with your index
    query_interface = QueryInterface(index=index)

    # Configure your QueryInterface
    query_interface.configure_retriever(similarity_top_k=100)
    query_interface.configure_response_synthesizer()
    query_interface.assemble_query_engine()

    return query_interface

def run_streamlit_app():
        
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

# Call the Streamlit run function with this module as the target
if "init" not in st.session_state:
    st.session_state.init = True
    query_interface = init_query_interface()
    st.session_state.query_engine = query_interface.query_engine

run_streamlit_app()