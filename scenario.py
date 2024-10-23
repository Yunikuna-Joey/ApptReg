# Utility imoprts
from zoneinfo import ZoneInfo
from dateutil import parser
from datetime import datetime

# Helper file imports
from emailService import createConfirmationMessage, createDeleteConfirmationMessage, sendEmail
from model import initializeChatModel, initializeClassificationModel
from helper import convertDateTime, displayConfirmationMessage, emailChecker, generatePrompt, phoneNumberChecker, carDescriptionchecker, serviceToHours, serviceTypeChecker, getInstagramUsername
from eventService import addEvent, checkWeekendCondition, checkDayState, checkWorkHour, createEventObject, deleteEvent, displayEventObjectInfo, getEventObjectById, isTimeAvailable, populateAvailableTimesMonth, populateEventsForDay

# database import 
from sessionManager import UserSession

# environment variables
from dotenv import load_dotenv
load_dotenv()
import os

def additionScenario(userId, userInput, databaseSession): 
    # intialize the chat model
    chatModel = initializeChatModel()  

    # grab the current user session
    session = UserSession.getUserSession(userId, databaseSession)

    # Create a new user session entry in the database if client is not already in the database
    if session is None: 
        # constructor class being called for default values associated with instagramUID
        instagramUsername = getInstagramUsername(userId, os.getenv('INSTAGRAM_UAT'))
        session = UserSession(userId, instagramUsername)
        databaseSession.add(session)
        databaseSession.commit()

    # debugging statement 
    print(f"This is the value of current user session {session}")

    # exit conditions 
    if userInput.lower().strip() in ['exit', 'quit', 'stop']: 
        return "Ending the conversation. Goodbye!"

    # initialize variables to current user session [references]
    intentObject = session.intentObject
    eventObject = session.eventObject 
    currentField = session.currentField

    # if there is not a valid intentObject, then create the model and determine the intent object [reduce redundant classification model intialization]
    if not intentObject:
        intentModel = initializeClassificationModel() 
        intentResponse = intentModel.generate_content(userInput)
        intentObject = intentResponse.text.strip()

        # save the intentObject entry with the generated response
        session.intentObject = intentObject
        # commit the change from None => intent value 
        databaseSession.commit()

    # if a create intent was made, execute logic for eventObject building to be added into the Google Calendar [session vars: intentObject, descriptionObject?, serviceDuration, currentField, confirmationShown, currentConfirmationField, eventObjectDict]
    if intentObject in ['create']: 
        # determine if there is a field in-progress 
        if currentField: 
            # Field validation
            if currentField == 'number': 
                # Error check with function here 
                if phoneNumberChecker(userInput) == False:
                    errorMessage = "I apologize, I didn't understand the phone number you provided. Please use the format 999-123-456"
                    return errorMessage, False 
                
                # Commit changes into the database 
                session.eventObject[currentField] = userInput
                session.currentField = None 
                databaseSession.commit()                                
            
            elif currentField == 'email': 
                # Error checking with function
                if emailChecker(userInput) == False: 
                    errorMessage = "I'm sorry, I didn't understand the email you entered. Please enter a valid email address that can receive emails."
                    return errorMessage, False

                # Commit changes into the database
                session.eventObject[currentField] = userInput
                session.currentField = None 
                databaseSession.commit()
            
            elif currentField == 'carModel': 
                # Error checking 
                if carDescriptionchecker(userInput) == False: 
                    errorMessage = "I apologize, I didn't understand the car year/make/model that you provided. Please provide your car in the format year/make/model. (Ex: 2015 Honda Civic)"
                    return errorMessage, False

                # Commit changes into the database 
                session.eventObject[currentField] = userInput 
                session.currentField = None 
                databaseSession.commit()                 
            
            elif currentField == 'description': 
                # Error checking 
                if serviceTypeChecker(userInput) == False: 
                    errorMessage = "That is not a service we offer. Please choose a service we offer: interior, exterior, or both."
                    return errorMessage, False

                # Modify the user input if they said both
                if 'both' in userInput or 'Both' in userInput: 
                    userInput = 'Exterior & Interior'
                    session.serviceDuration = serviceToHours(userInput)
                    session.eventObject[currentField] = userInput
                    session.currentField = None
                    databaseSession.commit()
                
                else: 
                    session.serviceDuration = serviceToHours(userInput)
                    session.eventObject[currentField] = userInput
                    session.currentField = None 
                    databaseSession.commit()
                
            elif currentField == 'start': 
                try: 
                    # we need a condition that retrieves the previous saved startTime in-memory from utilizing session management
                    startTime = parser.parse(userInput)

                    # Error checking the requested time 
                    if checkWeekendCondition(startTime) == False or checkDayState(startTime) == False or checkWorkHour(startTime) == False:
                        if checkWeekendCondition(startTime) == False: 
                            errorMessage = "Please choose a weekend as we are not taking appointments on weekdays."
                            return errorMessage, False
                        elif checkDayState(startTime) == False: 
                            errorMessage = "Please choose a valid day not in the past."
                            return errorMessage, False
                        elif checkWorkHour(startTime) == False: 
                            errorMessage = "Please choose a time within our working hours (8 AM - 8 PM)."
                            return errorMessage, False

                    # Gather all the events for the client-requested date
                    scheduledEventList = populateEventsForDay(startTime)
                    
                    # convert the requested start-time for comparison against the existing list of events 
                    newStartTime = startTime.astimezone(ZoneInfo("America/Los_Angeles"))

                    # error checking against the client requested time and already booked-time
                    if any(event['start']['dateTime'] == newStartTime.isoformat() for event in scheduledEventList):
                        errorMessage = "Your requested time is not available. Here are the available times"
                        availableTimeList = populateAvailableTimesMonth()

                        return errorMessage + "\n" + availableTimeList,  False
                    
                    # Push changes into database
                    session.eventObject[currentField] = startTime
                    session.currentField = None
                    databaseSession.commit()                        
                
                except(ValueError, TypeError): 
                    errorMessage = "I'm sorry, I didn't understand the date and time you provided. Please provide your desired appointment time and date in this format (September 18 at 10AM)"
                    return errorMessage, False

            else: 
                if 'facility' in userInput and currentField == 'location': 
                    userInput = 'Onsite Appointment'
                 
                session.eventObject[currentField] = userInput
                session.currentField = None
                databaseSession.commit()

        # Iterate through the user session's event object
        for field, value in eventObject.items(): 
            if value is None: 
                # set the current field for database session management
                session.currentField = field 
                databaseSession.commit()

                # generate a prompt for the missing field 
                prompt = generatePrompt(field)
                return prompt, False
        
        #*****************************Confirmation Section**************************************************
        # only create this map when all of the fields of the eventObject are not None [filled out]
        if all(value is not None for value in session.eventObject.values()): 
            # parse the database for the current client confirmation field 
            confirmationField = session.currentConfirmationField

            # return a confirmation message if the user has not seen a confirmation message 
            if session.confirmationShown is None:
                confirmationPrompt = "Is there anything you'd like to change in your appointment details? You can say things like 'change the car model' or 'update the email. If you are done making changes, simply say 'Done'."

                # Toggle the session to be true 
                session.confirmationShown = True 

                # This returns the message with all of the details parsed from the user and the prompt for the user to make a decision
                return confirmationPrompt + "\n" + displayConfirmationMessage(session.eventObject, session.serviceDuration), False
            
            # otherwise proceed with determining which field to edit and continue with story adding logic 
            else: 
                languageFieldMap = { 
                    'name': ['name', 'change name', 'update name'],
                    'number': ['phone', 'number', 'update phone', 'change number'],
                    'email': ['email', 'update email', 'change email'],
                    'carModel': ['car', 'update car', 'change car', 'car model'],
                    'location': ['location', 'change location', 'update location'],
                    'description': ['cleaning', 'service', 'description', 'change service', 'update cleaning'],
                    'start': ['time', 'date', 'appointment time', 'change time', 'change date'],
                }

                if confirmationField: 
                    # Field validation 
                    if confirmationField == 'number': 
                        if phoneNumberChecker(userInput) == False: 
                            errorMessage = "I apologize, I didn't understand the phone number you provided. Please use the format 999-123-4567"
                            return errorMessage, False
                        
                        session.eventObject[confirmationField] = userInput
                        session.currentConfirmationField = None
                        session.confirmationShown = None
                        databaseSession.commit()
                    
                    elif confirmationField == 'email': 
                        if emailChecker(userInput) == False: 
                            errorMessage = "I'm sorry, I didn't understand the email you entered. Please enter a valid email address that can receive emails."
                            return errorMessage, False
                        
                        session.eventObject[confirmationField] = userInput
                        session.currentConfirmationField = None 
                        session.confirmationShown = None
                        databaseSession.commit()

                    elif confirmationField == 'carModel': 
                        if carDescriptionchecker(userInput) == False: 
                            errorMessage = "I apologize, I didn't understand the car year/make/model that you provided. Please provide your car in the format year/make/model. (Ex: 2015 Honda Civic)"
                            return errorMessage, False
                    
                        session.eventObject[confirmationField] = userInput
                        session.currentConfirmationField = None 
                        session.confirmationShown = None
                        databaseSession.commit()
                    
                    elif confirmationField == 'description': 
                        # if we are changing the service type, we need to check if the allotted time is sufficient
                        prevDurationTime = session.serviceDuration

                        #* Determine if we can change the eventObject description before checking if the time is available
                        if 'both' in userInput or 'Both' in userInput: 
                            userInput = 'Exterior & Interior'
                            session.serviceDuration = serviceToHours(userInput)
                            session.eventObject[confirmationField] = userInput
                            session.currentConfirmationField = None 
                            # session.confirmationShown = None
                            databaseSession.commit()
                        #* Same objective as the if conditional
                        else: 
                            session.serviceDuration = serviceToHours(userInput)
                            session.eventObject[confirmationField] = userInput
                            session.currentConfirmationField = None 
                            # session.confirmationShown = None
                            databaseSession.commit()
                        
                        #* Fill in Later.
                        if session.serviceDuration > prevDurationTime:
                            # check if the current startTime is avaiable for the new duration 
                            if isTimeAvailable(eventObject['start'], session.serviceDuration) == False: 
                                errorMessage = f"Your new cleaning service could not be performed at your initial appointment time {convertDateTime(session.eventObject['start'], session.serviceDuration)}"
                                errorMessage2 = f"Please choose another time that works best for you as well as make sure there is enough time available to finish in ({session.serviceDuration} hours.)"

                                scheduledList = populateAvailableTimesMonth()
                                
                                #* The plan might be to just overwrite the user session's current confirmation field to be the field that handles checking for a valid time
                                session.currentConfirmationField = ['start']
                                databaseSession.commit()
                                return errorMessage + "\n" + errorMessage2 + "\n" + scheduledList, False
                        
                        else: 
                            # if we do not trigger the above conditional to pursue time story-line then we need a way to get back to reviewing the confirmation eventObject details 
                            session.confirmationShown = None
                            databaseSession.commit()
                            
                    elif confirmationField == 'start': 
                        try: 
                            startTime = parser.parse(userInput)

                            if checkWeekendCondition(startTime) == False or checkDayState(startTime) == False or checkWorkHour(startTime) == False:
                                if checkWeekendCondition(startTime) == False: 
                                    errorMessage = "Please choose a weekend as we are not taking appointments on weekdays."
                                    return errorMessage, False
                                elif checkDayState(startTime) == False: 
                                    errorMessage = "Please choose a valid day not in the past."
                                    return errorMessage, False
                                elif checkWorkHour(startTime) == False: 
                                    errorMessage = "Please choose a time within our working hours (8 AM - 8 PM)."
                                    return errorMessage, False
                            
                            scheduledEventList = populateEventsForDay(startTime)

                            newStartTime = startTime.astimezone(ZoneInfo("America/Los_Angeles"))

                            if any(event['start']['dateTime'] == newStartTime.isoformat() for event in scheduledEventList):
                                errorMessage = "Your requested time is not available. Here are the available times"
                                availableTimeList = populateAvailableTimesMonth()

                                return errorMessage + "\n" + availableTimeList, False
                            
                            # push changes into the database 
                            session.eventObject[confirmationField] = startTime 
                            session.currentConfirmationField = None 
                            session.confirmationShown = False
                            databaseSession.commit()
                        
                        except(ValueError, TypeError):
                            errorMessage = "I'm sorry, I didn't understand the date and time you provided. Please provide your desired appointment time and date in this format (September 18 at 10AM)"
                            return errorMessage, False
                    
                    else: 
                        if 'facility' in userInput and confirmationField == 'location': 
                            userInput = 'Onsite Appointment'
                        
                        session.eventObject[confirmationField] = userInput
                        session.currentConfirmationField = None 
                        session.confirmationShown = False
                        databaseSession.commit() 


                # iterate through the potential fields that the user wants to edit 
                for field, keywords in languageFieldMap.items(): 
                    # if the userInput matches a field to edit 
                    if any(keyword in userInput for keyword in keywords): 
                        # set the current confirmation field and then return the prompt associated with the field 
                        session.currentConfirmationField = field
                        databaseSession.commit()

                        prompt = generatePrompt(field)
                        #* There might be a clash of double available times with this and the confirmation 'start' case [test accordingly]
                        return prompt, False if field != 'start' else populateAvailableTimesMonth + '\n' + prompt, False
                    
                    #* Fill in this conditional for being finished with confirmation
                    elif userInput in ['done', 'Done', 'finished', 'finish']: 
                        # This will combine the username, number, email, carModel, and service description into one object 
                        descriptionObject = session.instagramUsername + "\n" + session.eventObject['number'] + "\n" + session.eventObject['email'] + "\n" + session.eventObject['carModel'] + "\n" + session.eventObject['description'] 
                        
                        # pack the event object together 
                        confirmationObject = createEventObject( 
                            session.eventObject['name'], 
                            session.eventObject['location'], 
                            descriptionObject, 
                            session.eventObject['start'], 
                            session.serviceDuration
                        )

                        # performs service of adding the event into the Calendar 
                        confirmationEvent = addEvent(confirmationObject)
                        uniqueEventId = confirmationEvent.get('id')

                        # store the message to send in an email 
                        confirmationMsg = createConfirmationMessage(
                            uniqueEventId, 
                            session.eventObject['name'], 
                            session.eventObject['email'], 
                            session.eventObject['number'],
                            session.eventObject['carModel'], 
                            session.eventObject['location'], 
                            session.eventObject['description'], 
                            session.eventObject['start'], 
                            session.serviceDuration
                        )

                        # performs the back-end service to send out the confirmation email with their confirmation code 
                        sendEmail(confirmationMsg, session.eventObject['email'])

                        # resetSessionObjectValues(session.intentObject)
                        # resetSessionObjectValues(session.descriptionObject)
                        # resetSessionObjectValues(session.eventObject)

                        successMessage = f"You have successfully booked your appointment for {convertDateTime(session.eventObject['start'], session.serviceDuration)}!"
                        return successMessage, True

                    #* Create a new conditional so that can catch 'bot does not understand and retry until it hits one of the above conditionals.'
                    else: 
                        errorMessage = "I did not understand that, please let me know which category you would like to change or reply with 'Done' to continue with scheduling your appointment"
                        return errorMessage, False

    # delete scenario  newImplementaiton: [intentObject, currentField, confirmation]
    elif intentObject in ['delete']: 
        if session.currentField is None: 
            session.currentField = 'awaitConfirmationCode'
            databaseSession.commit() 

            responseMessage = "Please provide your confirmation code found in the email that was sent to your inbox so I can find your appointment!"
            return responseMessage, False 
        
        elif session.currentField == "awaitConfirmationCode": 
            session.confirmationCode = userInput
            session.currentField = 'displayEventInfo'
            databaseSession.commit() 

            responseMessage = "This is the appointment I found with the confirmation code. Is this the appointment you would like to cancel?"
            requestedEventObject = getEventObjectById(session.confirmationCode)
            eventObjectInfo = displayEventObjectInfo(requestedEventObject)
            return responseMessage + eventObjectInfo, False
        
        elif session.currentField == "displayEventInfo": 
            if userInput.lower() in ['yes', 'correct', 'thats the one', 'yup', 'mhm']:
                requestedEventObject = getEventObjectById(session.confirmationCode)

                # pack the message before deleting the event 
                deleteMsgObject = createDeleteConfirmationMessage(
                    requestedEventObject['summary'],
                    (requestedEventObject['description'].split('\n'))[2], 
                    (requestedEventObject['description'].split('\n'))[3], 
                    (requestedEventObject['description'].split('\n'))[4], 
                    datetime.fromisoformat(requestedEventObject['start']['dateTime'])
                )

                # send out the email 
                sendEmail(deleteMsgObject, (requestedEventObject['description'].split('\n'))[2])
                
                # delete the event on the backend (service)
                deleteEvent(session.confirmationCode)

                # reset session variables 
                session.intentObject = None 
                session.currentField = None 
                session.confirmationCode = None
                databaseSession.commit()

                responseMessage = "You have successfully cancelled your appointment. I have also sent out an email about the appointment cancellation. Please feel free to book with us when you're ready!"
                return responseMessage, False
            
            # the event that the user replies with no 
            else: 
                session.intentObject = None 
                session.confirmationCode = None 
                session.currentField = None 
                databaseSession.commit()

                # respond normally and reset intent back to blank and restart delete storyline if necessary
                response = chatModel.generate_content(userInput).text
                return response, False

    else: 
        # reset if something was made
        if intentObject:
            session.intentObject = None 
            databaseSession.commit()
        response = chatModel.generate_content(userInput).text
        return response, False