from flask import Flask, render_template, request, jsonify
from chatbot import Chatbot
import google.generativeai as genai
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Initialize chatbot
chatbot = Chatbot()

# Configure Gemini API
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)
gemini_model = genai.GenerativeModel('gemini-pro')

# Career context for better responses
CAREER_CONTEXT = """
You are a career advisor specializing in technology careers. Your role is to provide:
1. Detailed, practical advice about tech careers
2. Specific examples and actionable steps
3. Current industry trends and insights
4. Personalized guidance based on the user's situation
5. Encouraging and supportive responses

Always maintain a professional yet friendly tone and focus on providing value to the user's career journey.
"""

def get_gemini_response(prompt):
    try:
        # Add career context to the prompt
        full_prompt = f"{CAREER_CONTEXT}\n\nUser Question: {prompt}\n\nPlease provide a detailed, helpful response focusing on career advice."
        response = gemini_model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"Error getting response from Gemini: {str(e)}"

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_input = data.get('message', '')
    
    if not user_input:
        return jsonify({'response': 'Please provide a message.'})
    
    # Try to get response from our trained model
    try:
        # Try to determine category from the prompt
        category = None
        career_categories = [
            "Career Exploration", "Resume and Cover Letter", "Job Search",
            "Skills Development", "Interview Preparation", "Career Growth",
            "Work-Life Balance", "Industry Trends", "Education and Training",
            "Career Transition"
        ]
        
        for cat in career_categories:
            if cat.lower() in user_input.lower():
                category = cat
                break
        
        response = chatbot.generate_response(user_input, category)
        
        # If response is too generic or empty, use Gemini
        if not response or "I can help you with this" in response:
            response = get_gemini_response(user_input)
    except Exception as e:
        # If there's any error with our model, use Gemini
        response = get_gemini_response(user_input)
    
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True) 