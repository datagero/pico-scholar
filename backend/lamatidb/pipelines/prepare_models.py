# Downloads and saves the models to be used by the system
# Called from docker builds

import os
from transformers import AutoModel, AutoTokenizer

def save_contiguous_model(model, save_path):
    for param in model.parameters():
        if not param.is_contiguous():
            param.data = param.data.contiguous()
    model.save_pretrained(save_path)

# Define the local path where the model should be saved
local_model_path = "persisted_models/allenai/scibert_scivocab_uncased"

# Check if the model exists locally
if not os.path.exists(local_model_path):
    print("Model not found locally. Downloading from allenai/scibert_scivocab_uncased...")
    model = AutoModel.from_pretrained("allenai/scibert_scivocab_uncased")
    # Save the model with tensors made contiguous
    os.makedirs(local_model_path, exist_ok=True)
    save_contiguous_model(model, local_model_path)
    # model.save_pretrained(local_model_path)
    tokenizer = AutoTokenizer.from_pretrained('allenai/scibert_scivocab_uncased')
    tokenizer.save_pretrained(local_model_path)

    print(f"Model saved locally at {local_model_path}")
