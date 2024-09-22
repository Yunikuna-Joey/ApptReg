""" 
    This is going to hold some code runs of different scenarios
"""
from zoneinfo import ZoneInfo
from eventService import checkDayState, createEventObject, addEvent, checkWeekendCondition, listAvailableTimeMonth, listAvailableTimeValidMonth, populateEventsForDay
from emailService import createConfirmationMessage, sendEmail
from helper import convertDateTime, resetObjectValues
from dateutil import parser
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

# successful run of adding event to calendar
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
                            # convert the user input into a naive datetime object 
                            startTime = parser.parse(userInput)
                            
                            #* Check if the requested day is a weekend
                                #* if not prompt the user to choose a different day
                            while checkWeekendCondition(startTime) == False and checkDayState(startTime) == False: 
                                print(f'[Teni]: Please choose a weekend as we are not taking appointments on weekdays at the moment.')
                                userInput = input("[You]: ")
                                startTime = parser.parse(userInput)
                            
                            #* if the day is a weekend and in the present | future, 
                                #* check if the timeslot is available 
                            """ 
                                First method to attempt: 
                                    1) gather all of the events on the requested day [done]
                                    2) convert the requested datetime object into .iso format
                                    3) initialize comparison between requested .iso format and iterate through the gathered events
                                    4) If the timeslot is available, then we can schedule the appointment [pack the eventObject with the requested time]
                                        4a) otherwise, list the available timeslots for that day, dependent on the type of requested service 
                                            [will need to implement the hashmap for service type : time required for service]
                            """

                            scheduledEventList = populateEventsForDay(startTime)
                            
                            # modStartTime = startTime
                            # newStartTime = modStartTime.replace(tzinfo=ZoneInfo('America/Los_Angeles'))
                            newStartTime = startTime.astimezone(ZoneInfo("America/Los_Angeles"))
                            
                            # checks for all the events in
                            while any(event['start']['dateTime'] == newStartTime.isoformat() for event in scheduledEventList): 
                                print(f"[Teni]: Your requested time is not available. Here are the available times")
                                # listAvailableTimeMonth(startTime)
                                listAvailableTimeValidMonth()
                                print("[Teni]: Please choose another time that works for you")
                                userInput = input("[You]: ")
                                startTime = parser.parse(userInput)
                                newStartTime = startTime.astimezone(ZoneInfo('America/Los_Angeles'))

                            #* This means we were able to pass the checks of being the correct day and having a valid timeslot
                            eventObject['start'] = startTime
                                
                        except (ValueError, TypeError): 
                            print("[Teni]: I'm sorry, I didn't understand the date and time you provided. Please provide your desired appointment time and date in this format (September 18 at 10AM)")
                            continue

                    else:  
                        # removes the trailing and leading whitespaces 
                        userInput.strip()
                        # print(f"This is the value of userInput {userInput}")
                        
                        # modifying/processing userInput 
                        if 'facility' in userInput:
                            userInput = 'Onsite Appointment'
                        
                        elif 'both' in userInput: 
                            userInput = 'Exterior & Interior'
                    
                        eventObject[field] = userInput

                print(f'This is the current values of eventObject {eventObject}')
            
            # Goes through all of the eventObject values to determine if all values are valid, true, [not None]
            if all(eventObject.values()):  
                descriptionObject += eventObject['description'] + "\n" + eventObject['carModel'] +  "\n" + eventObject['number'] + "\n" + eventObject['email']       
                
                # pack the eventObject 
                confirmationObject = createEventObject(
                    eventObject['name'], 
                    eventObject['location'], 
                    descriptionObject, 
                    eventObject['start']
                )
                # This will create the actual calendar event in the backend 
                addEvent(confirmationObject)

                # we will need to send a confirmation email to the customer after adding the event into google calendar
                confirmationMsg = createConfirmationMessage(eventObject['name'], eventObject['carModel'], eventObject['location'], eventObject['description'], eventObject['start'])
                # sendEmail(confirmationMsg, eventObject['email'])

                # we expect to see a [createEventObject] and [addEvent] message(s) here

                print(f"[Teni]: You have successfully booked your appointment for {convertDateTime(eventObject['start'])}!")

                # reset back to blank state after booking appointment
                resetObjectValues(intentObject)
                resetObjectValues(descriptionObject)
                resetObjectValues(eventObject)
                break
        
        # otherwise, respond back to user as normal [reset the intentObject if a non-valid one was made as well]
        else: 
            # reset the intent object 
            intentObject = ""
            response = model.generate_content(userInput)
            print(f"[Teni]: {response.text}")
            print(f"This is intentObject after resetting the value. {intentObject}")

# testing the time object (datetime type) within our confirmation message creation 
def testTime(): 
    print("Initializing the chat")
    userInput = input("[You]: ")

    time = parser.parse(userInput)
    msg = createConfirmationMessage("Joey", "vehicle information", "address", "interior", time)

    print(msg)

def testWhileLoop():
    userInput = ""
    while userInput not in ['exit', 'quit']:
        userInput = input("Type something: ")
        cleanStartTime = parser.parse(userInput)
        
        # populate the events for the requested day
        eventList = populateEventsForDay(cleanStartTime)
        modStartTime = cleanStartTime
        newStartTime = modStartTime.replace(tzinfo=ZoneInfo('America/Los_Angeles'))

        # iterate through the list of events for the requested day
        # if there is a match from the requested day/time with an event in the list
            # Notify the user that is the time is not available 
            # list the available times for the day 
            # break out of the for loop 
        # else: we proceed as normal 

        for event in eventList: 
            if newStartTime.isoformat() == event['start']['dateTime']: 
                print(f"[Teni]: Your requested time is not available. Please choose another time")
                listAvailableTimeMonth(cleanStartTime)
                break
            else: 
                print("We hit the else statement where nothing should happen besides the message")
            
        print('Done.')

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
        'location': "Please provide your address if you would like for us to come to you, otherwise enter 'your facility'. ",
        'description': "What kind of wash are you looking for? We have interior, exterior, or you can say both",
        'start': "What day and time are you lookin for? Please specify the date and time in this format 'September 18 at 12PM'",
    }

    return prompts.get(field, "Could you provide more information?")