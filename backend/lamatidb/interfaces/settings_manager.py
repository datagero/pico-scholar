import os
from llama_index.core import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

def set_local_llm():
    from llama_index.embeddings.llamafile import LlamafileEmbedding
    from llama_index.llms.llamafile import Llamafile
    from llama_index.core import Settings
    Settings.embed_model = LlamafileEmbedding(base_url="http://localhost:8080")
    Settings.llm = Llamafile(
        base_url="http://127.0.0.1:8080",
        temperature=0,
        seed=0
    )

    # response = Settings.llm.complete("Who is Laurie Voss? write in 10 words")

class SettingsManager:

    @staticmethod
    def set_global_settings(set_local=False):
        if set_local:
            set_local_llm()
        else:
            Settings.embed_model = HuggingFaceEmbedding(model_name="allenai/scibert_scivocab_uncased")

    @staticmethod
    def get_db_name():
        return os.environ['TIDB_DB_NAME']
