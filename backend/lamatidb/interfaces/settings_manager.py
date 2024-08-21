import os
from llama_index.core import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

class SettingsManager:

    @staticmethod
    def set_global_settings():
        # local_model_path = "persisted_models/allenai/scibert_scivocab_uncased"

        # def save_contiguous_model(model, save_path):
        #     for param in model.parameters():
        #         if not param.is_contiguous():
        #             param.data = param.data.contiguous()
        #     model.save_pretrained(save_path)

        # if not os.path.exists(local_model_path):
        #     os.makedirs(local_model_path)
        #     Settings.embed_model = HuggingFaceEmbedding(model_name="allenai/scibert_scivocab_uncased")
        #     save_contiguous_model(Settings.embed_model._model, local_model_path)
        # else:
        #     HuggingFaceEmbedding(model_name=local_model_path)

        Settings.embed_model = HuggingFaceEmbedding(model_name="allenai/scibert_scivocab_uncased")

    @staticmethod
    def get_db_name():
        return os.environ['TIDB_DB_NAME']
