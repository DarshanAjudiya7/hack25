from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

class Chatbot:
    def __init__(self, model_path="./chatbot_model"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = AutoModelForCausalLM.from_pretrained(model_path)
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)
    
    def generate_response(self, prompt, category=None):
        # Prepare the input text
        if category:
            input_text = f"Category: {category}\nPrompt: {prompt}\nResponse:"
        else:
            input_text = f"Prompt: {prompt}\nResponse:"
        
        # Tokenize the input
        inputs = self.tokenizer(input_text, return_tensors="pt").to(self.device)
        
        # Generate response
        with torch.no_grad():
            outputs = self.model.generate(
                inputs["input_ids"],
                max_length=200,
                num_return_sequences=1,
                no_repeat_ngram_size=2,
                temperature=0.7,
                top_k=50,
                top_p=0.95,
                pad_token_id=self.tokenizer.eos_token_id
            )
        
        # Decode and return the response
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        # Extract only the response part
        response = response.split("Response:")[-1].strip()
        return response

def main():
    chatbot = Chatbot()
    print("Chatbot initialized. Type 'quit' to exit.")
    
    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == 'quit':
            break
        
        # Try to determine category from the prompt
        category = None
        for cat in ["Coding", "Debugging", "Learning", "Problem Solving", "Testing", 
                   "Security", "Architecture", "DevOps", "Data Science", "Frontend", "Backend"]:
            if cat.lower() in user_input.lower():
                category = cat
                break
        
        response = chatbot.generate_response(user_input, category)
        print(f"\nBot: {response}")

if __name__ == "__main__":
    main() 