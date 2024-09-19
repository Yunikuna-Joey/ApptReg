#* Emailing purposes
from emailService import * 
from eventService import * 
from helper import *
from testrun import *

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

def main(): 
    print("Initializing the chat")

    model = initializeChatModel()
    intentModel = initializeClassificationModel()
    intentObject = ""
    eventObject = { 
        'summary': None, 
        'location': None, 
        'description': None, 
        'start': None, 
        'end': None
    }

    while True: 
        # Let user type in their responses
        userInput = input("[You]: ")

        # Bot will generate a response to the userInput
        response = model.generate_content(userInput)
        
        # Determine the intent behind the user input
        intentObject = intentModel.generate_content(userInput) 
        # print(f"[intentObject]: This is the intentObject {intentObject}")
        print(f"This is the intent Object {intentObject.text} and this is the lower {intentObject.text.lower()}")

        # if intentObject.text.lower().strip() == "appointment scheduling" or intentObject.text.lower().strip() == "create": 
        #     print("Hello world")

        # Reset the intent object if the intentObject is not one of the following options
        # if intentObject not in ['create', 'modify', 'delete']: 
        #     intentObject = "" 

        if intentObject.text.lower().strip() == "appointment scheduling" or intentObject.text.lower().strip() == "create": 
            print("I have triggered the create conditional")
            # Extract or prompt for missing information
            for field in eventObject:
                if not eventObject[field]:
                    # Generate a prompt to ask for missing information
                    prompt = generatePrompt(field)
                    print(f"[Teni]: {prompt}")
                    userInput = input("[You]: ")
                    eventObject[field] = model.generate_content(userInput).text.strip()

            # Call the function to create the event object
            object = createEventObject(
                eventObject['summary'],
                eventObject['location'],
                eventObject['description'],
                eventObject['start'], 
                eventObject['end']
            )

            addEvent(object)
            print("[Teni]: Your event has been created successfully!")

            # Reset the intent and event object after creating the event
            intentObject = ""
            eventObject = {key: None for key in eventObject}


        # Display the generated response
        # print(f'[Teni]: {response.text}')

        
    
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
    # main()
    # testRun()

    # displayAllEvents()
    # displayCurrWeekEvents()
    # displayWeekendEvents()
    # listAvailableTime()
    # testTime()

    # proto1()

    userInput = ""
    while userInput not in ['exit', 'quit']:
        userInput = input("Type something: ")
        startTime = parser.parse(userInput)
        checkWeekendCondition(startTime)

        if checkWeekendCondition(startTime): 
            finalList = populateEventsForDay(startTime)
            print(f"[Main Thread]: {finalList}")


