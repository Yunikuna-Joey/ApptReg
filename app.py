#* Emailing purposes
from emailService import * 
from eventService import * 
from classify import *
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
        system_instruction=os.getenv('SYSTEM_INSTRUCTION'),
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

def main(): 
    #* Test scenario 
        # create an eventObject 
        # add event into Calendar
        # send email about appointment confirmation
    # eventObject = createEventObject()
    # addEvent(eventObject)
    # messageObject = createConfirmationMessage()
    # sendEmail(messageObject, os.getenv('TEST_USER'))
    # displayAllEvents()
    # print("Hello world")
    # newStartTime = datetime.datetime(2024, 9, 1, 14, 0) # September 1 2024, 2:00 PM
    # newEndTime = datetime.datetime(2024, 9, 1, 15, 0)   # September 1 2024, 3:00 PM
    # editEvent("flq1ho9lfpan7ugr1mgjtedadk", newStartTime, newEndTime)
    # createDeleteConfirmationMessage(os.getenv('TEST_USER'))
    # createEditConfirmationMessage(os.getenv('TEST_USER'))

    print("Initializing the chat")
    model = initializeChatModel()
    intentModel = initializeClassificationModel()
    intentObject = ""
    while True: 
        # Register user input 
        userInput = input("[You]: ")

        # Enhance the exit conditions
        if userInput.lower() in ["exit", "quit", "stop"]: 
            print("[Ten]: Ending the conversation, Goodbye!")
            break

        # invoke a response from the chat model
        tenResponse = model.generate_content(userInput)

        # determine if user has declared some intent
        if not intentObject:
            intentObject = classifyUserAction(intentModel, userInput)
        else:
            processUserAction(intentObject)
            # if intentObject: 
            #     processUserAction(intentObject)

        print(f"[Bot]: {tenResponse.text}")

       

if __name__ == "__main__": 
    main()
