#* Emailing purposes
from emailService import * 
from eventService import * 
from helper import *
from testrun import *

from dotenv import load_dotenv
import os 
load_dotenv()

import requests
import google.generativeai as genai

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

#* Example request [refer back as necessary]
def exampleClientRequest():
    model = initializeChatModel()
    response = model.generate_content("What is the most popular food?")
    print(response.text)

def example(): 
    model = initializeChatModel()
    response = model.generate_content("Hello, I would like to schedule an appointment")
    print(response.text)

#* Potential helper function
def generatePrompt(field): 
    """ 
        This will allow for customization of different questions that can be asked 
        to fill in for the missing (necessary) information to pack the 
        event object 
    """

    prompts = {
        'name': "What is your name?",
        'number': "What is your phone number?",
        'email': "What is your email address?",
        'carModel': "What is the year/make/model of your vehicle?", 
        'location': "Do you need us to come to you or are you able to come to our establishment?",
        'description': "What kind of wash are you looking for? We have interior, exterior, or you can say both",
        'start': "What day and time are you lookin for? Please specify the date and time in this format 'September 18 at 12PM'",
    }

    return prompts.get(field, "Could you provide more information?")

# Instagram API URL to send messages
INSTAGRAM_API_URL = "https://graph.facebook.com/v21.0/me/messages"

def instagramReply(recipientId, messageContent): 
    url = f"{INSTAGRAM_API_URL}?access_token={os.getenv('INSTAGRAM_TOKEN')}"

    # payload for sending a message
    payload = { 
        'recipient': {'id': recipientId},
        'message': {'message': messageContent}
    }
    
    # pack reponse payload
    response = requests.post(url, json=payload)

    # success Code
    if response.status_code == 200: 
        print(f"Message sent to user {recipientId}: {messageContent}")
    
    else: 
        print(f"Failed to send message: {response.status_code}, {response.text}")

# This is the start of integrating the instagram account into the bot responses
def main(): 
    """" 
    ** background tasks before starting #1 
        we need to set-up Flask or node.js server so that our web hooks can live detect incoming end-user message requests to reply back to. 
        need to check-in with developer portal with IG api and continue 

    1. Try and send out a hard-coded response to an user input
        (need to look into webhooks for live account testing)
        --> Me (end-user) will send a greeting message to the account
        --> Bot will send a message 
    """ 
    print('hello world :(')

        

        
    
if __name__ == "__main__": 
    """
        The event object should visually look like 
            Customer Name
            Date/time of the appointment
            Address 
            Description ==> Type of wash  
                            Year/Make/Model  
                            Phone Number 
                            Email address 
    """
    #* our scenarios 
    # proto1() # add event scenario
    # proto2() # delete event scenario
    # proto3() # update event scenarios

    #** keep this as a basis for eventObject declaration
    eventObject = {
        'name': 'Hinata', 
        'number': '222-222-2222', 
        'email': 'testing@email.com', 
        'carModel': '2006 BMW 330i', 
        'location': 'Facility', 
        'description': 'Interior and Exterior', 
        'start': datetime(2024, 9, 21, 10, 15, 0)
    }

    messagePayload = {'entry': [{'id': '0', 'time': 1728281463, 'changes': [{'field': 'messages', 'value': {'sender': {'id': '12334'}, 'recipient': {'id': '23245'}, 'timestamp': '1527459824', 'message': {'mid': 'random_mid', 'text': 'random_text'}}}]}], 'object': 'instagram'}

    # entry = messagePayload.get('entry', [])[0]  
    # changes = entry.get('changes', [])[0]
    # message_value = changes.get('value', {})
    senderId = messagePayload['entry'][0]['changes'][0]['value']['sender']['id']
    # message = message_value.get('message', {})
    # message_text = message.get('text', '')  # The actual message text
    message_text = messagePayload['entry'][0]['changes'][0]['value']['message']['text']

    # print(f"This is the entry value {entry}")
    # print(f"This is the changes value {changes}")
    # print(f"This is message_value value {message_value}")
    print(f"This is the senderId {senderId}")
    # print(f"This is message value {message}")
    print(f"This is message_text {message_text}")
    
    

