import os
import csv
from sqlalchemy import URL
from llama_index.core import StorageContext, VectorStoreIndex, Document
from llama_index.core.storage.index_store import SimpleIndexStore
from llama_index.vector_stores.tidbvector import TiDBVectorStore
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import textwrap

def read_csv(file_path):
    data = []
    with open(file_path, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            data.append(row)
    return data

# Load your data
file_path = 'pubmed_sample/pubmed24n0541.csv'
content = read_csv(file_path)


# # Sample data from your content
# # If abstract is empty, then fill it with title
# for row in content:
#     if row[3] == '':
#         row[3] = row[1]

# Actually, to get better quality results, let's ignore the records without abstract for now
# remove records without abstract
content = [x for x in content if x[3] != '']


sample_dict = {x[0]: {'text' : x[3], 'title': x[1], 'authors': x[2], 'year': x[4]} for x in content[1:][:10]}
sample_text = [x['text'] for x in sample_dict.values()]


# Load database and create index
embedding_model = HuggingFaceEmbedding(model_name="allenai/scibert_scivocab_uncased")



# Function to predict labels for a list of texts
import torch
# Define the class labels based on your model's label mapping
# From https://huggingface.co/reginaboateng/pico_ner_adapter/blob/main/config.json
label2id = {
    0: "O",
    1: "I-INT",
    2: "I-OUT",
    3: "I-PAR"
}

def classify_texts(model, tokenizer, texts, threshold=0.7):
    # Prepare the model input
    encoded_inputs = tokenizer(texts, padding=True, truncation=True, max_length=512, return_tensors="pt", return_offsets_mapping=True)
    input_ids = encoded_inputs['input_ids'].to(model.device)
    attention_mask = encoded_inputs['attention_mask'].to(model.device)

    # Predict
    with torch.no_grad():
        outputs = model(input_ids, attention_mask=attention_mask)
        probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)

    # Apply threshold and convert predictions
    predictions = []
    for sequence_probs in probabilities:
        sequence_predictions = []
        for token_probs in sequence_probs:
            max_prob, predicted_label = torch.max(token_probs, dim=-1)
            if max_prob >= threshold:
                sequence_predictions.append(predicted_label.item())
            else:
                sequence_predictions.append(0)  # Classify as 'O' if below threshold
        predictions.append(sequence_predictions)

    return predictions, input_ids.cpu().numpy(), encoded_inputs['offset_mapping'].cpu().numpy()

    #     predictions = torch.argmax(outputs.logits, dim=-1)

    # return predictions.cpu().numpy(), input_ids.cpu().numpy(), encoded_inputs['offset_mapping'].cpu().numpy()

def extract_terms(tokenizer, predictions, input_ids, offset_mapping, label2id):
    # Initialize a list to store extracted terms for each sequence
    all_extracted_terms = []

    # Iterate over each sequence in the batch
    for i, sequence in enumerate(predictions):
        # Initialize a dictionary to store terms for each label in the current sequence
        extracted_terms = {label: [] for label in label2id.values()}
        
        # Convert input_ids to tokens
        tokens = tokenizer.convert_ids_to_tokens(input_ids[i])
        
        # Iterate over each token, prediction, and offset in the sequence
        for token, prediction, offset in zip(tokens, sequence, offset_mapping[i]):
            if token.startswith("##"):  # Handle WordPiece tokens
                # Append the subword token without '##' to the previous term
                if extracted_terms[label2id[prediction]]:
                    extracted_terms[label2id[prediction]][-1] += token[2:]
            else:
                if label2id[prediction] != "O":  # Skip 'O' (Outside) labels if not needed
                    start, end = offset
                    term = tokenizer.decode(input_ids[i][start:end]).strip()
                    extracted_terms[label2id[prediction]].append(term)
        
        # Add the extracted terms for this sequence to the list
        all_extracted_terms.append(extracted_terms)

    return all_extracted_terms

import re
def clean_extracted_terms(extracted_terms):
    cleaned_terms = {}
    unwanted_tokens = ['[PAD]', '[CLS]', '[SEP]']
    
    for label, terms in extracted_terms.items():
        # Filter out empty strings, short terms
        cleaned_label_terms = []
        for term in terms:

            # Replace unwanted tokens with an empty string
            for token in unwanted_tokens:
                term = term.replace(token, '').strip()

            if term and len(term) > 2 and term not in cleaned_label_terms:
                cleaned_label_terms.append(term)
        
        if cleaned_label_terms:
            cleaned_terms[label] = cleaned_label_terms
    
    return cleaned_terms


from adapters import AutoAdapterModel
import adapters

from transformers import AutoTokenizer

# Load the tokenizer corresponding to the model
tokenizer = AutoTokenizer.from_pretrained("allenai/scibert_scivocab_uncased")
model = AutoAdapterModel.from_pretrained("allenai/scibert_scivocab_uncased")


adapters.init(model)
adapter_name = model.load_adapter("reginaboateng/Compacter_SciBert_adapter_ner_pico_for_classification_task", source="hf", set_active=True)
model.set_active_adapters(adapter_name)

texts = sample_text
predictions, input_ids, offset_mapping = classify_texts(model, tokenizer, sample_text, threshold=0.2)

# Extract terms based on predictions
extracted_terms = extract_terms(tokenizer, predictions, input_ids, offset_mapping, label2id)
cleaned_terms = [clean_extracted_terms(x) for x in extracted_terms]






documents = [
    Document(
        text=values['text'],
        metadata={"source": doc_id,
                  "title": values['title'],
                  "authors": values['authors'],
                  "year": values['year']},
        # embedding=values['embedding'].tolist()  # Attach the precomputed embedding directly
    )
    for doc_id, values in sample_dict.items()
]

tidb_connection_url = URL(
    "mysql+pymysql",
    username=os.environ['TIDB_USERNAME'],
    password=os.environ['TIDB_PASSWORD'],
    host=os.environ['TIDB_HOST'],
    port=4000,
    database="test",
    query={"ssl_verify_cert": True, "ssl_verify_identity": True},
)


# Define the TiDB Vector Store
USER_NAME = os.environ['DEVELOPER_NAME']
VECTOR_TABLE_NAME = "scibert_test4"
tidbvec = TiDBVectorStore(
    connection_string=tidb_connection_url,
    table_name= '_'.join([USER_NAME, VECTOR_TABLE_NAME]),
    distance_strategy="cosine",
    vector_dimension=768, # SciBERT outputs 768-dimensional vectors
    drop_existing_table=False,
)


# ----
# Underlying tech
# -> TiDB Vector Seach
# -> Llama Index (e.g. Optional -> chunk doc)


# First Run: Create index
# Create the storage context and index
storage_context = StorageContext.from_defaults(vector_store=tidbvec)
# TiDB automatically persists the embeddings when you use it as your vector store.
index = VectorStoreIndex.from_documents(
    documents, 
    storage_context=storage_context, 
    embed_model=embedding_model,
    show_progress=True
)

# ### Currently cannot persist index, need to investigate further
# # # Persist index (ideally we want to persist into the database), check if there's native support 
# # like https://docs.llamaindex.ai/en/stable/module_guides/storing/index_stores/ or https://docs.llamaindex.ai/en/stable/api_reference/storage/index_store/simple/?h=simpleindexstore#llama_index.core.storage.index_store.SimpleIndexStore
# # storage_context.persist(persist_dir="pubmed_sample/lama_index")

# from llama_index.core import (
#     load_index_from_storage,
#     load_indices_from_storage,
#     load_graph_from_storage,
# )

# # Retrieve index from storage
# storage_context = StorageContext.from_defaults(vector_store=tidbvec, index_store=SimpleIndexStore.from_persist_dir(persist_dir="pubmed_sample/lama_index"))

# # don't need to specify index_id if there's only one index in storage context
# index = load_index_from_storage(storage_context)
# # indices = load_indices_from_storage(storage_context)  # loads all indices

# Example 1.1: Granular Retrieval and Synthesis (Experimental Similarity search, we probably want a pure service for this)
# Maybe we can use this as similarity/semantic search engine, but further experimentation is needed
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.postprocessor import SimilarityPostprocessor
from llama_index.core import VectorStoreIndex, get_response_synthesizer

# configure retriever
retriever = VectorIndexRetriever(
    index=index,
    similarity_top_k=100, #limit to top 100
)

# configure response synthesizer
response_synthesizer = get_response_synthesizer()

# assemble query engine
query_engine = RetrieverQueryEngine(
    retriever=retriever,
    response_synthesizer=response_synthesizer,
    node_postprocessors=[SimilarityPostprocessor(similarity_cutoff=None)],
)

# query
# response = query_engine.query("List all the titles of the articles mentioned in the documents.")
response = query_engine.query("Neurological and cerebral conditions.")
print(response)


# Example of inspecting similarity scores (depending on your specific setup)
for node in response.source_nodes:
    source = node.metadata['source']
    title = node.metadata.get('title')
    abstract = node.text
    similarity = node.score
    print(f"Document {source} Title: {title}, Similarity: {similarity}")
    # print(f"Abstract: {abstract}")


# 1.2: Optional -> Re-Ranking based on classification (Include/Exclude).


# Example 2: Build RAG from Index (e.g. Chatbot)

# Create a query engine based on the TiDB vector store
query_engine = index.as_query_engine(similarity_top_k=len(documents)*4)

# Example query
response = query_engine.query("what is isotherms?")
print(textwrap.fill(str(response), 100))


response = query_engine.query(
    "List all the titles of the books mentioned in the documents."
)
print(textwrap.fill(str(response), 100))



# You can also filter with metadata (if available)
from llama_index.core.vector_stores.types import (
    MetadataFilter,
    MetadataFilters,
)

# Example of filtering with metadata (adjust to your use case)
query_engine = index.as_query_engine(
    filters=MetadataFilters(
        filters=[
            MetadataFilter(key="source", value="16625676", operator="=="),
            # MetadataFilter(key="Patient", value="US Adults", operator="=="), # Practical example once we have PICO elements extracted...
        ]
    ),
    similarity_top_k=2,
)
response = query_engine.query("What is the specific focus of the documents?")
print(textwrap.fill(str(response), 100))




# Make PICO more human-readable
# Annotation Guides: https://github.com/BIDS-Xu-Lab/section_specific_annotation_of_PICO/blob/main/Annotation%20guidelines.pdf

# Filter each source
for i, source in enumerate(list(sample_dict.keys())[:1]):
    print(f"Source: {source}, PICO: {cleaned_terms[i]}")

    query_engine = index.as_query_engine(
        filters=MetadataFilters(
            filters=[
                MetadataFilter(key="source", value=source, operator="=="),
            ]
        ),
    )

    response = query_engine.query("For the given PICO Extraction (Patient, Intervention, Outcome) look at the source abstract and give me a short sentence that accurately represents PICO for the document. You should return a dictionary with \
                                  {'I-INT': [Generated Sentence Related to Intervention], 'I-PAR': [Generated Sentence Related to study Participant], 'I-OUT': [Generated Sentence Related to study Outputs]}")
    print(textwrap.fill(str(response), 100))

# Debug viewer
#sample_dict['16625676']['text']