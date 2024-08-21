from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core import VectorStoreIndex, get_response_synthesizer
from llama_index.core.vector_stores.types import MetadataFilter, MetadataFilters
from llama_index.core import Settings

class QueryInterface:
    def __init__(self, index):
        self.index = index

    def configure_retriever(self, similarity_top_k=100, metadata_filters=None):
        if metadata_filters:
            metadata_filters = MetadataFilters(filters=[MetadataFilter(**f) for f in metadata_filters])
    
        self.retriever = VectorIndexRetriever(
            index=self.index,
            similarity_top_k=similarity_top_k,
            embedding_model=Settings.embed_model,
            filters=metadata_filters,
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
        self.query_engine = self.index.as_query_engine(filters=metadata_filters, response_synthesizer=None)
        response = self.query_engine.query(query)
        return response

    def filter_by_similarity_score(self, nodes, similarity_cutoff=0.6):
        """
        Filters nodes based on a similarity score cutoff.
        
        Args:
        - nodes: List of nodes retrieved by the retriever.
        - similarity_cutoff: The minimum similarity score a node must have to be included.
        
        Returns:
        - List of filtered nodes.
        """
        return [node for node in nodes if node.score >= similarity_cutoff]