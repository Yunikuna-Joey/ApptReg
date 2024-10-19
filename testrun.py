""" 
    This is going to hold some code runs of different scenarios
"""
from datetime import datetime
from zoneinfo import ZoneInfo
from eventService import checkDayState, createEventObject, addEvent, checkWeekendCondition, deleteEvent, displayEventObjectInfo, editEmail, editNumber, editServiceType, editTimeSlot, editVehicle, getEventObjectById, isTimeAvailable, listAvailableTimeValidMonth, populateEventsForDay, checkWorkHour
from emailService import createConfirmationMessage, createDeleteConfirmationMessage, createEditConfirmationMessage, sendEmail
from helper import convertDateTime, displayConfirmationMessage, resetObjectValues, carDescriptionchecker, phoneNumberChecker, emailChecker, serviceToHours, serviceTypeChecker
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

# successful run of adding event to calendar [addition]
def proto1(): 
    """
    Need to add the service being requested : time that needs to be accounted for
    """
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
    serviceOffsetTime = 0

    while True: 
        userInput = input("[You]: ")

        # Exit conditions 
        if userInput.lower().strip() in ["exit", "quit", "stop"]: 
            print("[Ten]: Ending the conversation, Goodbye!")
            break
            
        # classifies whether or not a valid user intention was made [create, modify, delete]
        if not intentObject: 
            intentObject = intentModel.generate_content(userInput)

        print(f"This is the value of intentObject {intentObject.text.lower()}")

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
                    userInput.strip() # remove the leading and trailing whitespaces from the user input 
                    
                    #* Parses the start_time field 
                    if field == 'number': 
                        while phoneNumberChecker(userInput) == False: 
                            print("[Teni1]: I apologize, I didn't understand the phone number you provided. Please use the format 999-123-4567")
                            userInput = input("[You]: ").strip()
                        
                        eventObject[field] = userInput
                    
                    elif field == 'email': 
                        while emailChecker(userInput) == False: 
                            print("[Teni]: I'm sorry, I didn't understand the email you entered. Please enter a valid email address that can receive emails.")
                            userInput = input("[You]: ").strip()
                        
                        eventObject[field] = userInput

                    elif field == 'carModel':  
                        while carDescriptionchecker(userInput) == False:  
                            print("[Teni1]: I apologize, I didn't understand the car year/make/model that you provided. Please provide your car in the format year/make/model. (Ex: 2015 Honda Civic)")
                            userInput = input("[You]: ").strip()

                        
                        eventObject[field] = userInput

                    elif field == 'description': 
                        if 'both' in userInput or 'Both' in userInput: 
                            userInput = 'Exterior & Interior'
                            serviceList = userInput.split('&')
                            offsetTime = [serviceToHours(element.strip().lower()) for element in serviceList]
                            serviceOffsetTime = sum(offsetTime)
                            eventObject[field] = userInput
                            
                        else: 
                            serviceOffsetTime = serviceToHours(userInput)
                            eventObject[field] = userInput

                    elif field == 'start': 
                        try:
                            # convert the user input into a naive datetime object 
                            startTime = parser.parse(userInput)
                            
                            #* Check if the requested day is a weekend
                                #* if not prompt the user to choose a different day
                            while checkWeekendCondition(startTime) == False or checkDayState(startTime) == False or checkWorkHour(startTime) == False: 
                                if checkWeekendCondition(startTime) == False:
                                    print("[Teni]: Please choose a weekend as we are not taking appointments on weekdays.")
                                elif checkDayState(startTime) == False:
                                    print("[Teni]: Please choose a valid day not in the past.")
                                elif checkWorkHour(startTime) == False:
                                    print("[Teni]: Please choose a time within our working hours (8 AM - 8 PM).")
                                
                                listAvailableTimeValidMonth()
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
                            
                            newStartTime = startTime.astimezone(ZoneInfo("America/Los_Angeles"))
                            
                            # checks the requested time from the end user against all of the events in the eventList for the day 
                            while any(event['start']['dateTime'] == newStartTime.isoformat() for event in scheduledEventList): 
                                print(f"[Teni]: Your requested time is not available. Here are the available times")
    
                                listAvailableTimeValidMonth()
                                print("[Teni]: Please choose a date/time that works for you in the format: (September 22 at 12PM)")
                                userInput = input("[You]: ")
                                startTime = parser.parse(userInput)

                                while checkWeekendCondition(startTime) == False or checkDayState(startTime) == False or checkWorkHour(startTime) == False or isTimeAvailable(startTime, serviceOffsetTime) == False: 
                                    if checkWeekendCondition(startTime) == False:
                                        print("[Teni]: Please choose a weekend as we are not taking appointments on weekdays.")
                                    elif checkDayState(startTime) == False:
                                        print("[Teni]: Please choose a valid day not in the past.")
                                    elif checkWorkHour(startTime) == False:
                                        print("[Teni]: Please choose a time within our working hours (8 AM - 8 PM).")
                                    elif isTimeAvailable(startTime, serviceOffsetTime) == False: 
                                        print(f"[Teni]: That timeslot is not available for your service, please choose another time and/or day to fit your service duration ({serviceOffsetTime} hours)")

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
                        if 'facility' in userInput and field == 'location':
                            userInput = 'Onsite Appointment'
                        
                        if 'both' in userInput and field == 'description': 
                            userInput = 'Exterior & Interior'
                    
                        eventObject[field] = userInput

                print(f'This is the current values of eventObject {eventObject}')
                print(f"This is the current value of serviceOffsetHour {serviceOffsetTime}")

            # create a hashmap that maps the field to natural language 
            languageFieldMap = { 
                'name': ['name', 'change name', 'update name'],
                'number': ['phone', 'number', 'update phone', 'change number'],
                'email': ['email', 'update email', 'change email'],
                'carModel': ['car', 'update car', 'change car', 'car model'],
                'location': ['location', 'change location', 'update location'],
                'description': ['cleaning', 'service', 'description', 'change service', 'update cleaning'],
                'start': ['time', 'date', 'appointment time', 'change time', 'change date'],
            }

            #*********************************************CONFIRMATION SECTION************************************************************
            while userInput != 'done':
                # ensure that everything looks right to the user before packing the event object
                displayConfirmationMessage(eventObject, serviceOffsetTime) 

                print("[Teni]: Is there anything you'd like to change in your appointment details? You can say things like 'change the car model' or 'update the email. If you are done making changes, simply say 'Done'.")
                userInput = input('[You]: ').lower().strip()

                # iterate through key and values
                for field, keywords in languageFieldMap.items(): 
                    # if any of the keyword is in the user input [through looping throught the values]
                    if any(keyword in userInput for keyword in keywords): 
                        # generate the correct prompt for the field the user wants to edit 
                        prompt = generatePrompt(field)
                        print(f"[Teni]: {prompt}")

                        # provide the available times again if user is looking to re-do the time 
                        if field == 'start': 
                            listAvailableTimeValidMonth()

                        newInput = input("[You]: ")
                        newInput.strip() # remove the leading and trailing whitespaces before processing in our back-end functions

                        if field == 'number':
                            while not phoneNumberChecker(newInput):
                                print("[Teni]: Invalid phone number. Please enter a valid phone number (e.g., 999-123-4567).")
                                newInput = input("[You]: ").strip()
                            eventObject[field] = newInput
                        
                        elif field == 'email':
                            while not emailChecker(newInput):
                                print("[Teni]: Invalid email format. Please enter a valid email address.")
                                newInput = input("[You]: ").strip()
                            eventObject[field] = newInput

                        elif field == 'carModel':
                            while not carDescriptionchecker(newInput):
                                print("[Teni]: Invalid car format. Please enter in the format 'year/make/model' (e.g., 2015 Honda Civic).")
                                newInput = input("[You]: ").strip()
                            eventObject[field] = newInput
                        
                        elif field == 'description': 
                             # if we change the service type, we need to change the offset hours 
                            prevOffsetTime = serviceOffsetTime              # save a copy of the old duration 

                            # process differently if we switched to both
                            if 'both' in newInput or 'Both' in newInput: 
                                newInput = "Exterior & Interior" 
                                serviceList = newInput.split('&')
                                calculation = [serviceToHours(element.strip().lower()) for element in serviceList] 
                                serviceOffsetTime = sum(calculation)
                                eventObject[field] = userInput

                            else: 
                                serviceOffsetTime = serviceToHours(newInput)    
                            
                            print(f"prev: {prevOffsetTime}, new: {serviceOffsetTime}")
                            print(f"This is eventObject startTime during confirmation re-check {eventObject['start']}")

                            # if the new duration is greater than the previous 
                            if serviceOffsetTime > prevOffsetTime: 
                                # we need to check if the current startTime allows for the new duration without conflicts
                                    # if the current startTime does not allow for the new duration, then we prompt the user to also pick a new time 
                                    # otherwise, continue with just changing the service type from one to another 
                                if isTimeAvailable(eventObject['start'], serviceOffsetTime) == False: 
                                    print(f"[Teni]: Your new cleaning service could not be performed at your initial appointment time {convertDateTime(eventObject['start'], serviceOffsetTime)}")
                                    print(f"[Teni]: Please choose another time that works best for you as well as make sure there is enough time available to finish ({serviceOffsetTime} hours.)")
                                    
                                    # list the available times for this month from the concurrent day  
                                    listAvailableTimeValidMonth() 

                                    newUserInputTime = input("[You]: ").strip()
                                    newTime = parser.parse(newUserInputTime)

                                    while checkWeekendCondition(newTime) == False or checkDayState(newTime) == False or checkWorkHour(newTime) == False or isTimeAvailable(newTime, serviceOffsetTime) == False: 
                                        if checkWeekendCondition(newTime) == False:
                                            print("[Teni]: Please choose a weekend as we are not taking appointments on weekdays.")
                                        elif checkDayState(newTime) == False:
                                            print("[Teni]: Please choose a valid day not in the past.")
                                        elif checkWorkHour(newTime) == False:
                                            print("[Teni]: Please choose a time within our working hours (8 AM - 8 PM).")
                                        elif isTimeAvailable(newTime, serviceOffsetTime) == False: 
                                            print(f"[Teni]: That timeslot is not available for your service, please choose another time and/or day to fit your service duration ({serviceOffsetTime} hours)")

                                        newInput = input("[You]: ").strip()
                                        newTime = parser.parse(newInput)
                                
                                    eventObject['start'] = newTime
                            
                            # After we check and finish finding a valid time 
                            # update the service 
                            eventObject['description'] = newInput


                        elif field == 'start': 
                            try: 
                                startTime = parser.parse(newInput) 

                                # check if the requested day is a weekend 
                                while checkWeekendCondition(startTime) == False or checkDayState(startTime) == False or checkWorkHour(startTime) == False or isTimeAvailable(startTime, serviceOffsetTime) == False: 
                                    if checkWeekendCondition(startTime) == False:
                                        print("[Teni]: Please choose a weekend as we are not taking appointments on weekdays.")
                                    elif checkDayState(startTime) == False:
                                        print("[Teni]: Please choose a valid day not in the past.")
                                    elif checkWorkHour(startTime) == False:
                                        print("[Teni]: Please choose a time within our working hours (8 AM - 8 PM).")
                                    elif isTimeAvailable(startTime, serviceOffsetTime) == False: 
                                        print(f"[Teni]: That timeslot is not available for your service, please choose another time and/or day to fit your service duration ({serviceOffsetTime} hours)")

                                    newInput = input("[You]: ").strip()
                                    startTime = parser.parse(newInput)

                                scheduledEventList = populateEventsForDay(startTime)

                                newStartTime = startTime.astimezone(ZoneInfo("America/Los_Angeles"))

                                while any(event['start']['dateTime'] == newStartTime.isoformat() for event in scheduledEventList): 
                                    print(f"[Teni]: Your requested time is not available. Here are the available times")
                                    # listAvailableTimeMonth(startTime)
                                    listAvailableTimeValidMonth()
                                    print("[Teni]: Please choose a date/time that works for you in the format: (September 22 at 12PM)")
                                    newInput = input("[You]: ").strip()
                                    startTime = parser.parse(newInput)
                                    newStartTime = startTime.astimezone(ZoneInfo('America/Los_Angeles'))
                                
                                eventObject['start'] = startTime

                            except (ValueError, TypeError):
                                print("[Teni]: I'm sorry, I didn't understand the date and time you provided. Please provide your desired appointment time and date in this format (September 18 at 10AM)")
                                continue

                        else:
                            # For generic fields like name, location, etc.
                            eventObject[field] = newInput.strip()

                        print(f"[Teni]: The {field} has been updated.")
                             

            # Goes through all of the eventObject values to determine if all values are valid, true, [not None]
            if all(eventObject.values()):  
                descriptionObject += eventObject['description'] + "\n" + eventObject['carModel'] +  "\n" + eventObject['number'] + "\n" + eventObject['email']       
                
                # pack the eventObject 
                confirmationObject = createEventObject(
                    eventObject['name'], 
                    eventObject['location'], 
                    descriptionObject, 
                    eventObject['start'], 
                    serviceOffsetTime
                )
                # This will create the actual calendar event in the backend 
                confirmationEvent = addEvent(confirmationObject)
                uniqueEventId = confirmationEvent.get('id')

                #**************************************** Uncomment the send email function in production ***********************************************************
                confirmationMsg = createConfirmationMessage(
                    uniqueEventId, 
                    eventObject['name'], 
                    eventObject['email'], 
                    eventObject['number'],
                    eventObject['carModel'], 
                    eventObject['location'], 
                    eventObject['description'], 
                    eventObject['start'], 
                    serviceOffsetTime
                )
                sendEmail(confirmationMsg, eventObject['email'])

                print(f"[Teni]: You have successfully booked your appointment for {convertDateTime(eventObject['start'], serviceOffsetTime)}!")

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

# successful run of deleting event in calendar [delete]
def proto2(): 
    print("Initializing the delete event scenario chat")
    model = initializeChatModel() 
    intentModel = initializeClassificationModel() 
    intentObject = ""

    # plan out the delete event scenario before coding 
    """ 
        (
        Instead of asking for portions of the eventObject for verification, 
            lets generate a 6 digit unique code for each appointment for 
            each addition of an event during event Add. 

            in delete scenario, we reference the 6 digit code for the specific event as lookup

            in edit scenario, we will also reference the 6 digit code for the specific event as look up to determine which specific event
        )        
    """

    # determine if a delete intention was made
    while True: 
        # prompt the user for an input
        userInput = input("[You]: ")

        # if there is no intent
        if not intentObject: 
            intentObject = intentModel.generate_content(userInput)
        
        if intentObject.text.strip().lower() in ['delete']: 
            print("[Teni]: Please provide the confirmation code you received with your appointment email to help me find your appointment!")
            confirmationCode = input("[You]: ")
            eventObject = getEventObjectById(confirmationCode)

            eventObjectInfo = displayEventObjectInfo(eventObject)

            # we need to print out the event object 
            print(f"[Teni]: {eventObjectInfo}")
            print(f"[Teni]: This is what I found with the confirmation code. Is this the appointment you would like to cancel?")
            
            cancelConfirmationInput = input("[You]: ")

            # if cancelConfirmationInput is yes
            #   delete the appointment from the calendar
            #   send the delete confirmation email 
            if cancelConfirmationInput.strip().lower() in ['yes', 'correct', 'thats the one', 'yup', 'mhm']: 
                deleteEvent(confirmationCode) 
                deleteMsgObject = createDeleteConfirmationMessage(
                    eventObject['summary'],
                    (eventObject['description'].split('\n'))[3], 
                    (eventObject['description'].split('\n'))[1], 
                    (eventObject['description'].split('\n'))[0], 
                    datetime.fromisoformat(eventObject['start']['dateTime'])
                ) 
                print(f"This is the deleteMessageObject {deleteMsgObject}")
                sendEmail(deleteMsgObject, (eventObject['description'].split('\n'))[3]) 
                
            # otherwise, break out of the delete intent and revert back to retrieving intent grabbing            
            else: 
                intentObject = ""
                response = model.generate_content(cancelConfirmationInput)
                print(f"[Teni]: {response.text}")

        else: 
            # reset the intent object 
            intentObject = ""
            response = model.generate_content(userInput)
            print(f"[Teni]: {response.text}")
            
def proto3(): 
    """ 
    Prompt for an intent [modify, update] 
    ask for the confirmation code / eventId 
    change a field of the eventObject
    confirm the changes 
    push changes into system
    """
    print("Initializing the update event scenario chat")
    model = initializeChatModel() 
    intentModel = initializeClassificationModel() 
    intentObject = ""
    eventObject = {}
    # create a hashmap that maps the field to natural language 
    languageFieldMap = { 
        'name': ['name', 'change name', 'update name'],
        'number': ['phone', 'number', 'update phone', 'change number'],
        'email': ['email', 'update email', 'change email'],
        'carModel': ['car', 'update car', 'change car', 'car model'],
        'location': ['location', 'change location', 'update location'],
        'description': ['cleaning', 'service', 'description', 'change service', 'update cleaning'],
        'start': ['time', 'date', 'appointment time', 'change time', 'change date'],
    }

    while True: 
        # prompt the user for an input
        userInput = input("[You]: ")

        # if there is no intent
        if not intentObject: 
            intentObject = intentModel.generate_content(userInput)

        # if the intent is deemed as modify 
        if intentObject.text.strip().lower() in ['modify']:
            # keep prompting the user for a valid confirmation code to pack the event object 
            while not eventObject: 
                print("[Teni]: Please provide the confirmation code you received with your appointment email to help me find your appointment!") 
                confirmationCode = input("[You]: ")

                eventObject = getEventObjectById(confirmationCode)
                
                if not eventObject: 
                    print("There is no appointment with that confirmation code. Please check your code again.")

            eventObjectInfo = displayEventObjectInfo(eventObject)           # format the eventOBject info into readable
            print(f"[Teni]: {eventObjectInfo}")
            print(f"[Teni]: This is what I found with the confirmation code. Is this the appointment you would like to modify?") 
            
            editConfirmationInput = input("[You]: ")

            # confirming and determining the correct appointment to start modifying
            while editConfirmationInput not in ['yes', 'correct', 'thats the one', 'yup', 'mhm']:
                print("[Teni]: Please enter your confirmation code for your specific appointment! If you'd like to stop now, type 'done'")
                confirmationCode = input("[You]: ")

                # exit condition 
                if confirmationCode.strip().lower() == 'done':
                    print("[Teni]: Please come back when you find your appointment code!")
                    # reset the parmeters as we are breaking out of the modify intent
                    resetObjectValues(intentObject)
                    eventObject = {}
                    break 
                
                eventObject = getEventObjectById(confirmationCode)
                while not eventObject: 
                    print("[Teni]: There is no appointment with that code. Try again.")
                    confirmationCode = input("[You]: ")
                    eventObject = getEventObjectById(confirmationCode)
                
                print(f"[Teni]: {eventObjectInfo}")
                print(f"[Teni]: This is what I found with the confirmation code. Is this the appointment you would like to modify?") 
                editConfirmationInput = input("[You]: ")
            
            #* after the object is confirmed, parse the user on what they would like to change
            while userInput.strip().lower() not in ['done']:
                print("[Teni]: What would you like to change? If you are done, simply type 'done'")    
                userInput = input("[You]: ")

                # iterate through key and values
                for field, keywords in languageFieldMap.items(): 
                    # if any of the keyword is in the user input [through looping throught the values]
                    if any(keyword in userInput for keyword in keywords): 
                        # generate the correct prompt for the field the user wants to edit 
                        prompt = generatePrompt(field)
                        print(f"[Teni]: {prompt}")

                        # provide the available times again if user is looking to re-do the time 
                        if field == 'start': 
                            listAvailableTimeValidMonth()

                        newInput = input("[You]: ")
                        newInput.strip() # remove the leading and trailing whitespaces before processing in our back-end functions

                        if field == 'number':
                            while not phoneNumberChecker(newInput):
                                print("[Teni]: Invalid phone number. Please enter a valid phone number (e.g., 999-123-4567).")
                                newInput = input("[You]: ").strip()
                            
                            # print(f"[MAIN_THREAD]: This is the eventObject {eventObject}")

                            print("[Teni]: Changing the phone number now...")
                            editNumber(confirmationCode, newInput)
                            editMsgObject = createEditConfirmationMessage(
                                confirmationCode, 
                                eventObject['summary'],
                                eventObject['description'].split('\n')[3],
                                eventObject['description'].split('\n')[2],
                                eventObject['description'].split('\n')[1],
                                eventObject['location'],
                                eventObject['description'].split('\n')[0],
                                datetime.fromisoformat(eventObject['start']['dateTime']),
                                serviceToHours(1 if eventObject['description'][0] != 'Exterior & Interior' else 2)
                            )
                            sendEmail(editMsgObject, eventObject['description'].split('\n')[3])
                        
                        elif field == 'email':
                            while not emailChecker(newInput):
                                print("[Teni]: Invalid email format. Please enter a valid email address.")
                                newInput = input("[You]: ").strip()
                            
                            print("[Teni]: Changing the email address now...")
                            editEmail(confirmationCode, newInput)
                            editMsgObject = createEditConfirmationMessage(
                                confirmationCode, 
                                eventObject['summary'],
                                eventObject['description'].split('\n')[3],
                                eventObject['description'].split('\n')[2],
                                eventObject['description'].split('\n')[1],
                                eventObject['location'],
                                eventObject['description'].split('\n')[0],
                                datetime.fromisoformat(eventObject['start']['dateTime']),
                                serviceToHours(1 if eventObject['description'][0] != 'Exterior & Interior' else 2)
                            )
                            sendEmail(editMsgObject, eventObject['description'].split('\n')[3])


                        elif field == 'carModel':
                            while not carDescriptionchecker(newInput):
                                print("[Teni]: Invalid car format. Please enter in the format 'year/make/model' (e.g., 2015 Honda Civic).")
                                newInput = input("[You]: ").strip()
                            
                            print("[Teni]: Changing your vehicle now...")
                            editVehicle(confirmationCode, newInput)
                            editMsgObject = createEditConfirmationMessage(
                                confirmationCode, 
                                eventObject['summary'],
                                eventObject['description'].split('\n')[3],
                                eventObject['description'].split('\n')[2],
                                eventObject['description'].split('\n')[1],
                                eventObject['location'],
                                eventObject['description'].split('\n')[0],
                                datetime.fromisoformat(eventObject['start']['dateTime']),
                                serviceToHours(1 if eventObject['description'][0] != 'Exterior & Interior' else 2)
                            )
                            sendEmail(editMsgObject, eventObject['description'].split('\n')[3])

                        elif field == 'description': 
                            while not serviceTypeChecker(newInput): 
                                print("[Teni]: That is not a service we offer. Please choose a service we offer: interior, exterior, or both.")
                                newInput = input("[You]: ").strip().lower()
                                
                            # if we change the service type, we need to change the offset hours 
                            splitList = eventObject['description'].split('\n')              # [attr1, attr2, attr3, attr4]
                            print(f"This is splitList at the 0index {splitList[0]}")
                            prevOffsetTime = serviceToHours(splitList[0])              # save a copy of the old duration 

                            # process differently if we switched to both
                            if 'both' in newInput: 
                                newInput = "Exterior & Interior" 
                                serviceList = newInput.split('&')
                                calculation = [serviceToHours(element.strip().lower()) for element in serviceList] 
                                serviceOffsetTime = sum(calculation)
                                # eventObject[field] = userInput

                            else: 
                                serviceOffsetTime = serviceToHours(newInput)    
                            
                            print(f"This is the value of serviceOffsetTime {serviceOffsetTime} and prevOffsetTime{prevOffsetTime}")
                            # if the new duration is greater than the previous [changing from interior ==> both]
                            if serviceOffsetTime > prevOffsetTime: 
                                # we need to check if the current startTime allows for the new duration without conflicts
                                    # if the current startTime does not allow for the new duration, then we prompt the user to also pick a new time 
                                    # otherwise, continue with just changing the service type from one to another 
                                if isTimeAvailable(datetime.fromisoformat(eventObject['start']['dateTime']), serviceOffsetTime) == False: 
                                    print(f"[Teni]: Your new cleaning service could not be performed at your initial appointment time {convertDateTime(datetime.fromisoformat(eventObject['start']['dateTime']), serviceOffsetTime)}")
                                    print(f"[Teni]: Please choose another time that works best for you as well as make sure there is enough time available to finish ({serviceOffsetTime} hours.)")
                                    
                                    # list the available times for this month from the concurrent day  
                                    listAvailableTimeValidMonth() 

                                    newUserInputTime = input("[You]: ").strip()
                                    newTime = parser.parse(newUserInputTime)

                                    while checkWeekendCondition(newTime) == False or checkDayState(newTime) == False or checkWorkHour(newTime) == False or isTimeAvailable(newTime, serviceOffsetTime) == False: 
                                        if checkWeekendCondition(newTime) == False:
                                            print("[Teni]: Please choose a weekend as we are not taking appointments on weekdays.")
                                        elif checkDayState(newTime) == False:
                                            print("[Teni]: Please choose a valid day not in the past.")
                                        elif checkWorkHour(newTime) == False:
                                            print("[Teni]: Please choose a time within our working hours (8 AM - 8 PM).")
                                        elif isTimeAvailable(newTime, serviceOffsetTime) == False: 
                                            print(f"[Teni]: That timeslot is not available for your service, please choose another time and/or day to fit your service duration ({serviceOffsetTime} hours)")

                                        newInput = input("[You]: ").strip()
                                        newTime = parser.parse(newInput)

                                    # to be added into the editServiceType function 
                                    # parameterStartTime = newTime.astimezone(ZoneInfo('America/Los_Angeles')).isoformat()
                                    editTimeSlot(confirmationCode, newTime, serviceOffsetTime)

                            # [changing from both ==> interior]
                            # if the time was valid for both, it is automatically valid for every service 
                            # so we just need to change the end time of the appointment in the back-end 
                            elif serviceOffsetTime < prevOffsetTime:
                                editTimeSlot(confirmationCode, datetime.fromisoformat(eventObject['start']['dateTime']), serviceOffsetTime)


                            # After we check and finish finding a valid time 
                            #* official publish to the back end calendar
                            # splitList[0] = newInput
                            # # to be added into the editServiceType function
                            # parameterDescription = '\n'.join(splitList)
                            editServiceType(confirmationCode, newInput)

                        elif field == 'start': 
                            try: 
                                startTime = parser.parse(newInput) 

                                # extract the duration from the eventObject
                                splitList = eventObject['description'].split('\n')
                                duration = splitList[0]

                                # check if the requested day is a weekend 
                                while checkWeekendCondition(startTime) == False or checkDayState(startTime) == False or checkWorkHour(startTime) == False or isTimeAvailable(startTime, serviceToHours(duration)) == False: 
                                    if checkWeekendCondition(startTime) == False:
                                        print("[Teni]: Please choose a weekend as we are not taking appointments on weekdays.")
                                    elif checkDayState(startTime) == False:
                                        print("[Teni]: Please choose a valid day not in the past.")
                                    elif checkWorkHour(startTime) == False:
                                        print("[Teni]: Please choose a time within our working hours (8 AM - 8 PM).")
                                    elif isTimeAvailable(startTime, serviceOffsetTime) == False: 
                                        print(f"[Teni]: That timeslot is not available for your service, please choose another time and/or day to fit your service duration ({serviceToHours(duration)} hours)")

                                    newInput = input("[You]: ").strip()
                                    startTime = parser.parse(newInput)

                                scheduledEventList = populateEventsForDay(startTime)

                                newStartTime = startTime.astimezone(ZoneInfo("America/Los_Angeles"))

                                while any(event['start']['dateTime'] == newStartTime.isoformat() for event in scheduledEventList): 
                                    print(f"[Teni]: Your requested time is not available. Here are the available times")
                                    # listAvailableTimeMonth(startTime)
                                    listAvailableTimeValidMonth()
                                    print("[Teni]: Please choose a date/time that works for you in the format: (September 22 at 12PM)")
                                    newInput = input("[You]: ").strip()
                                    startTime = parser.parse(newInput)
                                    newStartTime = startTime.astimezone(ZoneInfo('America/Los_Angeles'))
                                
                                editTimeSlot(confirmationCode, newStartTime, serviceToHours(duration))

                            except (ValueError, TypeError):
                                print("[Teni]: I'm sorry, I didn't understand the date and time you provided. Please provide your desired appointment time and date in this format (September 18 at 10AM)")
                                continue

                        else:
                            # For generic fields like name, location, etc.
                            eventObject[field] = newInput.strip()

                        print(f"[Teni]: The {field} has been updated.")

        else: 
            # reset the intent object 
            intentObject = ""
            response = model.generate_content(userInput)
            print(f"[Teni]: {response.text}")
        
    

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
                # listAvailableTimeMonth(cleanStartTime)
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