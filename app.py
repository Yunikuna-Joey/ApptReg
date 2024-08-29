from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build 

from dotenv import load_dotenv
import os 
import google.generativeai as genai

load_dotenv()

#* Global registration variables 
apiKey = os.getenv('API_TOKEN')
genai.configure(api_key=apiKey)
model = genai.GenerativeModel(os.getenv('API_MODEL'))

#* Service account registration
SCOPES = ['https://www.googleapis.com/auth/calendar']


#* Example request [refer back as necessary]
def exampleClientRequest():
    response = model.generate_content("What is the most popular food?")
    print(response.text)

def example(): 
    response = model.generate_content("Hello, I would like to schedule an appointment")
    print(response.text)

if __name__ == "__main__": 
    example()

