import google.generativeai as genai

from dotenv import load_dotenv
import os 
load_dotenv()

#* Instructions to connect the chat model with its instructions
def initializeChatModel(): 
    #* Global registration variables 
    apiKey = os.getenv('API_TOKEN')
    genai.configure(api_key=apiKey)

    model_config = { 
        'temperature': 1, 
        'top_p': 0.95, 
        'top_k': 64, 
        'max_output_tokens': 8192, 
        'response_mime_type': 'text/plain'
    }

    model = genai.GenerativeModel(
        model_name=os.getenv('API_MODEL'), 
        generation_config=model_config, 
        system_instruction=os.getenv('SYSTEM_INSTRUCTION1'),
    )

    print('[initializeChatModel]: Primary chat model initialized.')
    return model

def initializeClassificationModel(): 
    apiKey = os.getenv('API_TOKEN')
    genai.configure(api_key=apiKey)

    model_config = { 
        'temperature': 1, 
        'top_p': 0.95, 
        'top_k': 64, 
        'max_output_tokens': 8192, 
        'response_mime_type': 'text/plain'
    }
    
    model = genai.GenerativeModel(
        model_name=os.getenv('API_MODEL'), 
        generation_config=model_config, 
        system_instruction=os.getenv('CLASSIFICATION_INSTRUCTION'),
    )

    print("[initializeClassificationModel]: Model created successfully.")
    return model