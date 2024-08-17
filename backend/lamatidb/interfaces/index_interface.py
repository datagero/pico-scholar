import os
import time
from typing import List
from sqlalchemy import URL
from llama_index.core import StorageContext, VectorStoreIndex, Document
from llama_index.vector_stores.tidbvector import TiDBVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import Settings


class IndexInterface:
    def __init__(self, db_name: str, vector_table_name: str, embedding_model_name: str=None):
        self.db_name = db_name
        self.vector_table_name = vector_table_name
        self.index = None

        if embedding_model_name:
            self.embedding_model = HuggingFaceEmbedding(model_name=embedding_model_name)
        else:
            self.embedding_model = Settings.embed_model

        # Define the TiDB Connection and Vector Store
        self.tidb_connection_url = URL(
            "mysql+pymysql",
            username=os.environ['TIDB_USERNAME'],
            password=os.environ['TIDB_PASSWORD'],
            host=os.environ['TIDB_HOST'],
            port=4000,
            database=db_name,
            query={"ssl_verify_cert": True, "ssl_verify_identity": True},
        )

        self.tidbvec = TiDBVectorStore(
            connection_string=self.tidb_connection_url,
            table_name= self.vector_table_name,
            distance_strategy="cosine",
            vector_dimension=768, # SciBERT outputs 768-dimensional vectors
            drop_existing_table=False,
        )

        # Set the storage context for Llama Index. Llama will use this context to store the documents, embeddings and index.
        # TiDB automatically persists the embeddings when you use it as your vector store.
        self.storage_context = StorageContext.from_defaults(vector_store=self.tidbvec)

    def get_index(self):
        return self.index

    def load_index_from_vector_store(self):
        """
        Load index from vector store.
        Note it will load even if not exists
        """
        start_time = time.time()
        self.index = VectorStoreIndex.from_vector_store(
            vector_store=self.tidbvec,
            embed_model=self.embedding_model
        )

        # End timing
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Time taken to load the index: {elapsed_time:.2f} seconds")

    def load_index_if_exists(self):
        """
        Note - no longer using this as loading index directly from vector store
        Keeping as it may become useful when managing multiple indexes
        """
        index_structs = self.storage_context.index_store.index_structs()

        if index_structs:
            # Default to just get one index for now
            index_struct = index_structs[0]

            start_time = time.time()
            self.index = VectorStoreIndex(
                storage_context=self.storage_context,
                embed_model=self.embedding_model,
                index_struct=index_struct  # Provide the index structure here
            )

            # End timing
            end_time = time.time()
            elapsed_time = end_time - start_time
            print(f"Time taken to load the index: {elapsed_time:.2f} seconds")

    def create_index(self, documents:List[Document]):
        assert isinstance(documents, list), "Documents must be a list of Document objects"

        # Load data and create index
        start_time = time.time()
        self.index = VectorStoreIndex.from_documents(
            documents, 
            storage_context=self.storage_context, 
            embed_model=self.embedding_model,
            show_progress=True
        )
        # End timing
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Time taken to create the index: {elapsed_time:.2f} seconds")