import torch
from transformers import AutoTokenizer
from adapters import AutoAdapterModel
import adapters
import openai
import re

# Define the class labels based on your model's label mapping
label2id = {
    0: "O",
    1: "I-INT",
    2: "I-OUT",
    3: "I-PAR"
}

class PICO:
    def __init__(self, model_name="allenai/scibert_scivocab_uncased", adapter_name="reginaboateng/Compacter_SciBert_adapter_ner_pico_for_classification_task"):
        self.model_name = model_name
        self.adapter_name = adapter_name

        # Load the tokenizer corresponding to the model
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoAdapterModel.from_pretrained(self.model_name)

        adapters.init(self.model)
        self.adapter = self.model.load_adapter(self.adapter_name, source="hf", set_active=True)
        self.model.set_active_adapters(self.adapter)

    def classify_texts(self, texts, threshold=0.7):
        encoded_inputs = self.tokenizer(texts, padding=True, truncation=True, max_length=512, return_tensors="pt", return_offsets_mapping=True)
        input_ids = encoded_inputs['input_ids'].to(self.model.device)
        attention_mask = encoded_inputs['attention_mask'].to(self.model.device)

        # Predict
        with torch.no_grad():
            outputs = self.model(input_ids, attention_mask=attention_mask)
            probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)

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

    def extract_terms(self, predictions, input_ids, offset_mapping):
        all_extracted_terms = []
        for i, sequence in enumerate(predictions):
            extracted_terms = {label: [] for label in label2id.values()}
            tokens = self.tokenizer.convert_ids_to_tokens(input_ids[i])

            for token, prediction, offset in zip(tokens, sequence, offset_mapping[i]):
                if token.startswith("##"):  # Handle WordPiece tokens
                    if extracted_terms[label2id[prediction]]:
                        extracted_terms[label2id[prediction]][-1] += token[2:]
                else:
                    if label2id[prediction] != "O":  # Skip 'O' (Outside) labels
                        start, end = offset
                        term = self.tokenizer.decode(input_ids[i][start:end]).strip()
                        extracted_terms[label2id[prediction]].append(term)

            all_extracted_terms.append(extracted_terms)
        return all_extracted_terms

    def clean_extracted_terms(self, extracted_terms):
        cleaned_terms = {}
        unwanted_tokens = ['[PAD]', '[CLS]', '[SEP]']

        for label, terms in extracted_terms.items():
            cleaned_label_terms = []
            for term in terms:
                for token in unwanted_tokens:
                    term = term.replace(token, '').strip()

                if term and len(term) > 2 and term not in cleaned_label_terms:
                    cleaned_label_terms.append(term)

            if cleaned_label_terms:
                cleaned_terms[label] = cleaned_label_terms

        return cleaned_terms

    def enhance_text(self, texts, cleaned_terms):
        # Example enhancement logic
        enhanced_texts = []

        client = openai.Client()

        for i, terms in enumerate(cleaned_terms):
            prompt = f"""For the given PICO Extraction (Patient, Intervention, Outcome) look at the source abstract and give me a short sentence that accurately represents PICO for the document. 
You should return a dictionary with {{'I-INT': 'Generated Sentence Related to Intervention', 'I-PAR': 'Generated Sentence Related to study Participant', 'I-OUT': 'Generated Sentence Related to study Outputs'}}.
The PICO terms are: {terms}
The full abstract is: {texts[i]}"""
            completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
            generated_text = completion.choices[0].message.content


            # Regular expression to match the key-value pairs
            pattern = r"'(.*?)':\s*'(.*?)'"

            # Find all matches
            matches = re.findall(pattern, generated_text)

            # Convert matches to a dictionary
            result_dict = {key: value for key, value in matches}
            enhanced_texts.append(result_dict)

        return enhanced_texts

class Metadata:
    def __init__(self):
        self.pico = PICO()

    def process_text(self, texts):
        predictions, input_ids, offset_mapping = self.pico.classify_texts(texts, threshold=0.7)
        extracted_terms = self.pico.extract_terms(predictions, input_ids, offset_mapping)
        cleaned_terms = [self.pico.clean_extracted_terms(x) for x in extracted_terms]
        enhanced_terms = self.pico.enhance_text(texts, cleaned_terms)
        return cleaned_terms, enhanced_terms

# Debug viewer
#sample_dict['16625676']['text']
# Example Usage:
if __name__ == "__main__":
    sample_text = ["Sample input text for PICO classification and extraction. The participants are 22 years old and sufffer diabetes. and the intervention worked fantastically.",
                   "I cannot believe the outcome work the way it did. The participants were school kids and the intervention was a success."]

    metadata = Metadata()
    processed_terms, enhanced_terms = metadata.process_text(sample_text)

    print("Processed PICO terms:", processed_terms)
    print("Enhanced PICO terms:", enhanced_terms)
