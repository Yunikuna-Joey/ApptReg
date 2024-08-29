from dotenv import load_dotenv
import os 
import google.generativeai as genai

load_dotenv()


apiKey = os.getenv('API_TOKEN')
genai.configure(api_key=apiKey)


#* Example request [refer back as necessary]
def exampleClientRequest():
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("Write a story about a magic backpack.")
    print(response.text)
