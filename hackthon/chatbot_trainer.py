import json
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer
from datasets import Dataset
import torch

def load_prompts(file_path):
    prompts = []
    current_category = None
    
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if line.startswith('# '):
                current_category = line[2:]
            elif line and line[0].isdigit():
                # Extract the prompt text between quotes
                prompt = line.split('"')[1]
                prompts.append({
                    'category': current_category,
                    'prompt': prompt,
                    'response': f"This is a {current_category} related question. I can help you with this."
                })
    
    return prompts

def prepare_dataset(prompts):
    # Convert prompts to dataset format
    dataset = Dataset.from_dict({
        'category': [p['category'] for p in prompts],
        'prompt': [p['prompt'] for p in prompts],
        'response': [p['response'] for p in prompts]
    })
    return dataset

def train_chatbot():
    # Load prompts
    prompts = load_prompts('prompts.txt')
    
    # Prepare dataset
    dataset = prepare_dataset(prompts)
    
    # Initialize tokenizer and model
    model_name = "gpt2"  # You can use other models like "facebook/opt-350m"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(model_name)
    
    # Tokenize dataset
    def tokenize_function(examples):
        # Combine prompt and response
        texts = [f"Category: {cat}\nPrompt: {p}\nResponse: {r}" 
                for cat, p, r in zip(examples['category'], 
                                   examples['prompt'], 
                                   examples['response'])]
        return tokenizer(texts, padding="max_length", truncation=True, max_length=512)
    
    tokenized_dataset = dataset.map(tokenize_function, batched=True)
    
    # Training arguments
    training_args = TrainingArguments(
        output_dir="./chatbot_model",
        num_train_epochs=3,
        per_device_train_batch_size=4,
        save_steps=1000,
        save_total_limit=2,
    )
    
    # Initialize trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized_dataset,
    )
    
    # Train the model
    trainer.train()
    
    # Save the model
    trainer.save_model("./chatbot_model")
    tokenizer.save_pretrained("./chatbot_model")

if __name__ == "__main__":
    train_chatbot() 