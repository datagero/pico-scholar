from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core import VectorStoreIndex, get_response_synthesizer
from llama_index.core.vector_stores.types import MetadataFilter, MetadataFilters

class QueryInterface:
    def __init__(self, index):
        self.index = index

    def configure_retriever(self, similarity_top_k=100):
        self.retriever = VectorIndexRetriever(
            index=self.index,
            similarity_top_k=similarity_top_k
        )

    def configure_response_synthesizer(self):
        self.response_synthesizer = get_response_synthesizer()

    def assemble_query_engine(self, similarity_cutoff=None):
        self.query_engine = RetrieverQueryEngine(
            retriever=self.retriever,
            response_synthesizer=self.response_synthesizer,
            node_postprocessors=[SimilarityPostprocessor(similarity_cutoff=similarity_cutoff)],
        )

    def perform_query(self, query: str):
        response = self.query_engine.query(query)
        return response

    def inspect_similarity_scores(self, source_nodes):
        for node in source_nodes:
            source = node.metadata['source']
            title = node.metadata.get('title')
            similarity = node.score
            print(f"Document {source} Title: {title}, Similarity: {similarity}")

    def build_rag_query_engine(self, similarity_top_k=None):
        self.query_engine = self.index.as_query_engine(similarity_top_k=similarity_top_k)

    def perform_metadata_filtered_query(self, query: str, filters: list):
        metadata_filters = MetadataFilters(filters=[MetadataFilter(**f) for f in filters])
        self.query_engine = self.index.as_query_engine(filters=metadata_filters)
        response = self.query_engine.query(query)
        return response

    def generate_pico_summary(self, source: str, query: str):
        """ Experimental function, as this should be done at preprocessing stage (to enhance metadata before indexing)"""
        self.query_engine = self.index.as_query_engine(
            filters=MetadataFilters(filters=[MetadataFilter(key="source", value=source, operator="==")])
        )
        response = self.query_engine.query(query)
        return response
