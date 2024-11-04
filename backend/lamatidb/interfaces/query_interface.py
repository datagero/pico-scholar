import openai # Temporarily as paid LLM
# from together import Together
from llama_index.core.retrievers import VectorIndexRetriever, QueryFusionRetriever

from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core import VectorStoreIndex, get_response_synthesizer
from llama_index.core.vector_stores.types import MetadataFilter, MetadataFilters
from llama_index.core import Settings
from llama_index.core.llms import ChatMessage
from llama_index.llms.together import TogetherLLM


class QueryInterface:
    def __init__(self, index):
        self.index = index
        self.open_ai_client = None # Some actions for our demo require OpenAI's API for simplicity, planning to replace with local LLM
        self.llm = None # Migrating to llm setup instead of OpenAI

    def configure_openai_client(self):
        self.open_ai_client = openai.Client()
        # self.open_ai_client = Together()

    def configure_llm(self):
        # Demo to configure different LLMs -- currently not enabled
        # self.llm = TogetherLLM(
        #     model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo"
        # )
        return
    
    def get_query_gen_prompt(self):
        QUERY_GEN_PROMPT = (
            "You are a helpful assistant that generates multiple search queries based on a "
            "single input query. The input queries are related to medical field. Generate {num_queries} search queries "
            "related to the following input query:\n"
            "Query: {query}\n"
            "Queries:\n"
        )
        return QUERY_GEN_PROMPT
    
    def configure_retriever(self, similarity_top_k=100, metadata_filters=None):
        if metadata_filters:
            metadata_filters = MetadataFilters(filters=[MetadataFilter(**f) for f in metadata_filters])
    
        self.retriever = VectorIndexRetriever(
            index=self.index,
            similarity_top_k=similarity_top_k,
            embedding_model=Settings.embed_model,
            filters=metadata_filters if metadata_filters else None,
        )

    def configure_advanced_retriever(self, similarity_top_k=100, metadata_filters=None, num_queries = 4):
        if metadata_filters:
            metadata_filters = MetadataFilters(filters=[MetadataFilter(**f) for f in metadata_filters])
    
        index_retriever = VectorIndexRetriever(
            index=self.index,
            similarity_top_k=similarity_top_k,
            embedding_model=Settings.embed_model,
            filters=metadata_filters,
        )
        
        self.retriever = QueryFusionRetriever(
            [index_retriever],
            similarity_top_k=similarity_top_k,
            num_queries=num_queries,  # set this to 1 to disable query generation
            mode="reciprocal_rerank",
            use_async=True,
            verbose=True,
            query_gen_prompt=self.get_query_gen_prompt(),  # we could override the query generation prompt here
        )

    def configure_response_synthesizer(self):
        if not self.llm:
            self.configure_llm()
            
        self.response_synthesizer = get_response_synthesizer(llm=self.llm)

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
            text = node.text[:60]
            print(f"Document {source} Title: {title}, Similarity: {similarity}, Text: {text}")

    def build_rag_query_engine(self, similarity_top_k=None):
        self.query_engine = self.index.as_query_engine(similarity_top_k=similarity_top_k)

    def perform_metadata_filtered_query(self, query: str, filters: list):
        metadata_filters = MetadataFilters(filters=[MetadataFilter(**f) for f in filters])
        self.query_engine = self.index.as_query_engine(filters=metadata_filters, llm=self.llm)
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
    
    def query_chatgpt(self, chatgpt_prompt, model="gpt-3.5-turbo"):

        if not self.open_ai_client:
            self.configure_openai_client()

        # Step 2: Send the prompt to ChatGPT
        completion = self.open_ai_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": chatgpt_prompt}
                ]
            )
        generated_text = completion.choices[0].message.content

        return generated_text

    def query_llm(self, query):
        if not self.llm:
            self.configure_llm()

        messages = [
            ChatMessage(
                role="user", content=query
            )
        ]
        response = self.llm.chat(messages)
        return response.message.content
