from eventService import * 
from emailService import * 
from classify import *
import datetime
from app import initializeChatModel, initializeClassificationModel

def testRun(): 
    eventObject = createEventObject()
    addEvent(eventObject)
    messageObject = createConfirmationMessage()
    sendEmail(messageObject, os.getenv('TEST_USER'))
    displayAllEvents()
    print("Hello world")
    newStartTime = datetime.datetime(2024, 9, 1, 14, 0) # September 1 2024, 2:00 PM
    newEndTime = datetime.datetime(2024, 9, 1, 15, 0)   # September 1 2024, 3:00 PM
    editEvent("flq1ho9lfpan7ugr1mgjtedadk", newStartTime, newEndTime)
    createDeleteConfirmationMessage(os.getenv('TEST_USER'))
    createEditConfirmationMessage(os.getenv('TEST_USER'))

def run1(): 
    print("Initializing the chat")

    model = initializeChatModel()
    intentModel = initializeClassificationModel()
    intentObject = ""

    while True: 
        # Register user input 
        userInput = input("[You]: ")
        
        # Exit conditions
        if userInput.lower() in ["exit", "quit", "stop"]: 
            print("[Ten]: Ending the conversation, Goodbye!")
            break

        # determine if user has declared some intent
        if not intentObject:
            intentObject = classifyUserAction(intentModel, userInput)

        # invoke a response from the chat model
        tenResponse = model.generate_content(userInput)

        # This is the actual bot reponse to the user input
        print(f"[Ten]: {tenResponse.text}")

def run2(): 
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
            while intentObject == 'create': 
                print("[Teni]: What address is this car located at?")
                location = input("[You]: ")
                print("[Teni]: What day and time are you looking for?")
                dayPref = input("[You]: ")
                print("[Teni]: What type of car do you have? (Sedan, Coupe, Truck, SUV... etc)")
                carType = input("[You]: ")
                print("[Teni]: What is the year, make, and model of your car?")
                carModel = input("[You]: ")
                print("[Teni]: What type of cleaning are you looking for? (Interior, exterior, both)") 
                cleanType = input("[You]: ")
                print("[Teni]: Is there any pet hair that we should worry about? (Yes or no)")
                petHair = input("[You]: ")

                createEventObject(carModel, location, cleanType, dayPref)
        else:
            processUserAction(intentObject)
            # if intentObject: 
            #     processUserAction(intentObject)

        print(f"[Bot]: {tenResponse.text}")

def run3(): 
    print("Initializing the chat")
    intent = ""
    model = initializeChatModel()
    event_info = {}  # Dictionary to store event details

    while True:
        # Register user input
        userInput = input("[You]: ")

        # Exit condition
        if userInput.lower() in ["exit", "quit", "stop"]:
            print("[Ten]: Ending the conversation, Goodbye!")
            break

        # Let the LLM determine the intent and respond accordingly
        if not intent:
            response = model.generate_content(f"User said: '{userInput}'. What does the user want to do?")
            intent = response.text  # Capture intent from the LLM response

        if intent == "schedule an appointment":
            # Prompt for missing event information
            if 'summary' not in event_info:
                event_info['summary'] = input("[Ten]: What is the title of the event?")
            if 'location' not in event_info:
                event_info['location'] = input("[Ten]: Where is the event location?")
            if 'description' not in event_info:
                event_info['description'] = input("[Ten]: Please provide a description of the event.")
            if 'start' not in event_info:
                start_time = input("[Ten]: When does the event start? (format: YYYY-MM-DDTHH:MM:SS)")
                event_info['start'] = {
                    'dateTime': start_time,
                    'timeZone': 'America/Los_Angeles',  # Adjust timezone as needed
                }
            if 'end' not in event_info:
                end_time = input("[Ten]: When does the event end? (format: YYYY-MM-DDTHH:MM:SS)")
                event_info['end'] = {
                    'dateTime': end_time,
                    'timeZone': 'America/Los_Angeles',  # Adjust timezone as needed
                }

            # Check if all information is gathered
            if all(key in event_info for key in ['summary', 'location', 'description', 'start', 'end']):
                # Create the event object and add it to the calendar
                try:
                    addEvent(event_info)
                    print("[Ten]: Your appointment has been scheduled successfully.")
                    intent = ""  # Reset intent after scheduling
                    event_info = {}  # Reset event information for the next interaction
                except Exception as e:
                    print(f"[Ten]: There was an error scheduling your appointment: {e}")
        else:
            # Continue with the regular chatbot response
            tenResponse = model.generate_content(userInput)
            print(f"[Bot]: {tenResponse.text}")