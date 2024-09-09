#* Emailing purposes
from emailService import * 
from eventService import * 
from classify import *
from testrun import *
import datetime 

from dotenv import load_dotenv
import os 
load_dotenv()

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
def generate_prompt(field):
    """
    Generate a custom prompt based on the missing field.
    """
    prompts = {
        'location': "What address is this car located at?",
        'dayPref': "What day and time are you looking for?",
        'carType': "What type of car do you have? (Sedan, Coupe, Truck, SUV... etc)",
        'carModel': "What is the year, make, and model of your car?",
        'cleanType': "What type of cleaning are you looking for? (Interior, exterior, both)",
        'petHair': "Is there any pet hair that we should worry about? (Yes or no)"
    }
    return prompts.get(field, "Could you provide more information?")

def main(): 
    print("Initializing the chat")

    model = initializeChatModel()
    intentModel = initializeClassificationModel()
    intentObject = ""

    while True: 
        # Let user type in their responses
        userInput = input("[You]: ")

        # Bot will generate a response to the userInput
        response = model.generate_content(userInput)
        
        # Determine the intent behind the user input
        intentObject = intentModel.generate_content(userInput) 
        print(f"[intentObject]: This is the intentObject {intentObject}")
        print(f"This is the intent Object {intentObject.text} and this is the lower {intentObject.text.lower()}")

        if intentObject.text.lower().strip() == "appointment scheduling": 
            print("Hello world")

        # Reset the intent object if the intentObject is not one of the following options
        # if intentObject not in ['create', 'modify', 'delete']: 
        #     intentObject = "" 

        # if intentObject.text.lower() == 'appointment scheduling':
        #     print("I have triggered the create conditional")
        #     # Extract or prompt for missing information
        #     for field in eventObject:
        #         if not eventObject[field]:
        #             # Generate a prompt to ask for missing information
        #             prompt = generate_prompt(field)
        #             print(f"[Teni]: {prompt}")
        #             userInput = input("[You]: ")
        #             eventObject[field] = model.generate_content(userInput).text.strip()

        #     # Call the function to create the event object
        #     object = createEventObject(
        #         eventObject['carModel'],
        #         eventObject['location'],
        #         eventObject['cleanType'],
        #         eventObject['dayPref']
        #     )

        #     addEvent(object)
        #     print("[Teni]: Your event has been created successfully!")

        #     # Reset the intent and event object after creating the event
        #     intentObject = ""
        #     eventObject = {key: None for key in eventObject}


        # Display the generated response
        # print(f'[Teni]: {response.text}')

        
    
if __name__ == "__main__": 
    main()
