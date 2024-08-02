# Taken from https://haystack.deepset.ai/tutorials/27_first_rag_pipeline
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

from datasets import load_dataset
from haystack import Document
from haystack import Pipeline
from haystack.components.embedders import SentenceTransformersDocumentEmbedder
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.components.embedders import SentenceTransformersTextEmbedder
from haystack.components.retrievers.in_memory import InMemoryEmbeddingRetriever
from haystack.components.builders import PromptBuilder
from haystack.components.generators import OpenAIGenerator

# is the simplest DocumentStore to get started with.
# It requires no external dependencies and it’s a good option for smaller projects and debugging. 
# But it doesn’t scale up so well to larger Document collections, so it’s not a good choice for production systems
document_store = InMemoryDocumentStore()
embedding_model = 'sentence-transformers/all-MiniLM-L6-v2'

# Fetch the Data
dataset = load_dataset("bilgeyucel/seven-wonders", split="train")
docs = [Document(content=doc["content"], meta=doc["meta"]) for doc in dataset]

# Initalize a Document Embedder
doc_embedder = SentenceTransformersDocumentEmbedder(model=embedding_model)
doc_embedder.warm_up()

# Write Documents to the DocumentStore
docs_with_embeddings = doc_embedder.run(docs)
document_store.write_documents(docs_with_embeddings["documents"])

# initialise text embedder and retriever
text_embedder = SentenceTransformersTextEmbedder(model=embedding_model)
retriever = InMemoryEmbeddingRetriever(document_store)

# Define a Template Prompt
template = """
Given the following information, answer the question.

Context:
{% for document in documents %}
    {{ document.content }}
{% endfor %}

Question: {{question}}
Answer:
"""

prompt_builder = PromptBuilder(template=template)

# You can replace OpenAIGenerator in your pipeline with another Generator. Check out the full list of generators here.
# Generators are responsible for generating text after you give them a prompt. They are specific for each LLM technology (OpenAI, local, TGI and others).
if "OPENAI_API_KEY" not in os.environ:
    from getpass import getpass
    os.environ["OPENAI_API_KEY"] = getpass("Enter OpenAI API key:")
generator = OpenAIGenerator(model="gpt-3.5-turbo")


# Build the pipeline
# The pipelines in Haystack 2.0 are directed multigraphs of different Haystack components and integrations.
# Add all components to your pipeline and connect them

#  Create connections from text_embedder’s “embedding” output to “query_embedding” input of retriever, 
# from retriever to prompt_builder and from prompt_builder to llm. 
# Explicitly connect the output of retriever with “documents” input of the prompt_builder 
# to make the connection obvious as prompt_builder has two inputs (“documents” and “question”).

basic_rag_pipeline = Pipeline()
# Add components to your pipeline
basic_rag_pipeline.add_component("text_embedder", text_embedder)
basic_rag_pipeline.add_component("retriever", retriever)
basic_rag_pipeline.add_component("prompt_builder", prompt_builder)
basic_rag_pipeline.add_component("llm", generator)

# Now, connect the components to each other
basic_rag_pipeline.connect("text_embedder.embedding", "retriever.query_embedding")
basic_rag_pipeline.connect("retriever", "prompt_builder.documents")
basic_rag_pipeline.connect("prompt_builder", "llm")


# Asking a question
# Make sure to provide the question to both the text_embedder and the prompt_builder. 
# This ensures that the {{question}} variable in the template prompt gets replaced with your specific question.

question = "What does Rhodes Statue look like?"
response = basic_rag_pipeline.run({"text_embedder": {"text": question}, "prompt_builder": {"question": question}})
print(response["llm"]["replies"][0])

# Other example questions
examples = [
    "Where is Gardens of Babylon?",
    "Why did people build Great Pyramid of Giza?",
    "What does Rhodes Statue look like?",
    "Why did people visit the Temple of Artemis?",
    "What is the importance of Colossus of Rhodes?",
    "What happened to the Tomb of Mausolus?",
    "How did Colossus of Rhodes collapse?",
]