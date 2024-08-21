import os
import streamlit.web.bootstrap
import streamlit.config as _config
import webbrowser



def run(pmid):
    current_directory = os.path.dirname(__file__)
    pmid_file_name = "pmid.txt"
    pmid_file_path = os.path.join(current_directory, pmid_file_name)
# Open the file in write mode and save the content
    with open(pmid_file_path, "w") as file:
        file.write(pmid)
    
    webbrowser.open('http://localhost:8501')
    _config.set_option("server.headless", True)
    args = []

    st_file = "streamlit_app.py"
    # Get the full path of the adjacent file
    st_file_path = os.path.join(current_directory, st_file)
    streamlit.web.bootstrap.run(st_file_path,False,args,{})
#run("16626815")