from eventService import createEventObject, addEvent 
from emailService import createConfirmationMessage, sendEmail
from helper import convertDateTime 
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

# successful addition to the calendar run 
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
                            # going to need a check to determine if the time slot is available, otherwise, print out the available times
                            # in lieu of customer initial time request
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
                sendEmail(confirmationMsg, eventObject['email'])

                # we expect to see a [createEventObject] and [addEvent] message(s) here

                print(f"[Teni]: You have successfully booked your appointment for {convertDateTime(eventObject['start'])}!")
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

# testing the time object (datetime type) within our confirmation message creation 
def testTime(): 
    print("Initializing the chat")
    userInput = input("[You]: ")

    time = parser.parse(userInput)
    msg = createConfirmationMessage("Joey", "vehicle information", "address", "interior", time)

    print(msg)

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