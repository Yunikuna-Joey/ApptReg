from eventService import * 
from emailService import * 
from classify import *
from dateutil import parser
import datetime
from app import initializeChatModel, initializeClassificationModel

def testRun(): 
    eventObject = createEventObject()
    addEvent(eventObject)
    # messageObject = createConfirmationMessage()
    # sendEmail(messageObject, os.getenv('TEST_USER'))
    # displayAllEvents()
    # print("Hello world")
    # newStartTime = datetime.datetime(2024, 9, 1, 14, 0) # September 1 2024, 2:00 PM
    # newEndTime = datetime.datetime(2024, 9, 1, 15, 0)   # September 1 2024, 3:00 PM
    # editEvent("flq1ho9lfpan7ugr1mgjtedadk", newStartTime, newEndTime)
    # createDeleteConfirmationMessage(os.getenv('TEST_USER'))
    # createEditConfirmationMessage(os.getenv('TEST_USER'))

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

def proto1(): 
    print('Initializing the chat')
    
    model = initializeChatModel()
    intentModel = initializeClassificationModel() 
    intentObject = ""
    eventObject = { 
        'name': None,
        'number': None,
        'email': None,
        'carModel': None, 
        'location': None, 
        'description': None, 
        'start': None, 
    }
    descriptionObject = ""

    while True: 
        userInput = input("[You]: ")

        # Exit conditions 
        if userInput.lower().strip() in ["exit", "quit", "stop"]: 
            print("[Ten]: Ending the conversation, Goodbye!")
            break
            

        # classifies whether or not a valid user intention was made [create, modify, delete]
        if not intentObject: 
            intentObject = intentModel.generate_content(userInput)

        # if there was a 'create' intention then do something
        if intentObject.text.lower().strip() in ['create', 'appointment scheduling']: 
            # iterate over the eventObject items 
            for field, value in eventObject.items(): 
                if value == None: 
                    # generate a question to extract information from the user
                    prompt = generatePrompt(field)
                    print(f'[Teni]: {prompt}')

                    # invoke the user to input the missing information
                    userInput = input("[You]: ")
                    
                    #* Parses the start_time field 
                    if field == 'start': 
                        try: 
                            startTime = parser.parse(userInput)
                            print(startTime)
                            eventObject['start'] = startTime

                        except (ValueError, TypeError): 
                            print("[Teni]: I'm sorry, I didn't understand the date and time you provided. Please provide your desired appointment time and date in this format (September 18 at 10AM)")
                            continue
                    
                    #* thoughts about using another LLM prompt to extract the information and pack event object

                    else:  
                        eventObject[field] = userInput.strip()

                print(f'This is the current values of eventObject {eventObject}')
            
            # Goes through all of the eventObject values to determine if all values are valid, true, [not None]
            if all(eventObject.values()):         
                # pack the eventObject 
                confirmationObject = createEventObject(
                    eventObject['summary'], 
                    eventObject['location'], 
                    eventObject['description'], 
                    eventObject['start']
                )
                # This will create the actual calendar event in the backend 
                addEvent(confirmationObject)

                # we expect to see a [createEventObject] and [addEvent] message(s) here

                print("[Teni]: You have successfully booked your appointment for convert_datetime_object back to natural language")
                break

            # response = model.generate_content(userInput)
            # print(f"[Teni]: {response.text}")
            # print('[proto1]: I have triggered a create intention conditional.')
        
        # otherwise, respond back to user as normal [reset the intentObject if a non-valid one was made as well]
        else: 
            # reset the intent object 
            intentObject = ""
            response = model.generate_content(userInput)
            print(f"[Teni]: {response.text}")
            print(f"This is intentObject after resetting the value. {intentObject}")


# This function allows for question prompting the end user based on the information that we need 
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