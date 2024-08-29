from dotenv import load_dotenv
import os 
import google.generativeai as genai

load_dotenv()

#* Global registration variables 
apiKey = os.getenv('API_TOKEN')
genai.configure(api_key=apiKey)
model = genai.GenerativeModel(os.getenv('API_MODEL'))


#* Example request [refer back as necessary]
def exampleClientRequest():
    response = model.generate_content("What is the most popular food?")
    print(response.text)

