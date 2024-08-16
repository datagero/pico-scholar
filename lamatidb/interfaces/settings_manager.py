import os
from llama_index.core import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

class SettingsManager:
    @staticmethod
    def set_global_settings():
        Settings.embed_model = HuggingFaceEmbedding(model_name="allenai/scibert_scivocab_uncased")

    @staticmethod
    def get_db_name():
        return os.environ['TIDB_DB_NAME']