#Placeholder for PICO metadata pipelines


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


