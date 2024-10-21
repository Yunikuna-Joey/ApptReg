# Utility imoprts
from zoneinfo import ZoneInfo
from dateutil import parser

# Helper file imports
from model import initializeChatModel, initializeClassificationModel
from helper import displayConfirmationMessage, emailChecker, generatePrompt, phoneNumberChecker, carDescriptionchecker, serviceToHours, serviceTypeChecker, getInstagramUsername
from eventService import checkWeekendCondition, checkDayState, checkWorkHour, populateAvailableTimesMonth, populateEventsForDay

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
        return "Ending the converstaion. Goodbye!"

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

    # if a create intent was made, execute logic for eventObject building to be added into the Google Calendar
    if intentObject in ['create', 'appointment scheduling']: 
        # determine if there is a field in-progress 
        if currentField: 
            # Field validation
            if currentField == 'number': 
                # Error check with function here 
                if phoneNumberChecker(userInput) == False:
                    errorMessage = "I apologize, I didn't understand the phone number you provided. Please use the format 999-123-456"
                    return errorMessage
                
                # Commit changes into the database 
                session.eventObject[currentField] = userInput
                session.currentField = None 
                databaseSession.commit()                                
            
            elif currentField == 'email': 
                # Error checking with function
                if emailChecker(userInput) == False: 
                    errorMessage = "I'm sorry, I didn't understand the email you entered. Please enter a valid email address that can receive emails."
                    return errorMessage

                # Commit changes into the database
                session.eventObject[currentField] = userInput
                session.currentField = None 
                databaseSession.commit()
            
            elif currentField == 'carModel': 
                # Error checking 
                if carDescriptionchecker(userInput) == False: 
                    errorMessage = "I apologize, I didn't understand the car year/make/model that you provided. Please provide your car in the format year/make/model. (Ex: 2015 Honda Civic)"
                    return errorMessage

                # Commit changes into the database 
                session.eventObject[currentField] = userInput 
                session.currentField = None 
                databaseSession.commit()                 
            
            elif currentField == 'description': 
                # Error checking 
                if serviceTypeChecker(userInput) == False: 
                    errorMessage = "That is not a service we offer. Please choose a service we offer: interior, exterior, or both."
                    return errorMessage

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
                            return errorMessage
                        elif checkDayState(startTime) == False: 
                            errorMessage = "Please choose a valid day not in the past."
                            return errorMessage
                        elif checkWorkHour(startTime) == False: 
                            errorMessage = "Please choose a time within our working hours (8 AM - 8 PM)."
                            return errorMessage

                    # Gather all the events for the client-requested date
                    scheduledEventList = populateEventsForDay(startTime)
                    
                    # convert the requested start-time for comparison against the existing list of events 
                    newStartTime = startTime.astimezone(ZoneInfo("America/Los_Angeles"))

                    # error checking against the client requested time and already booked-time
                    if any(event['start']['dateTime'] == newStartTime.isoformat() for event in scheduledEventList):
                        errorMessage = "Your requested time is not available. Here are the available times"
                        availableTimeList = populateAvailableTimesMonth()

                        return errorMessage + "\n" + availableTimeList
                    
                    # Push changes into database
                    session.eventObject[currentField] = startTime
                    session.currentField = None
                    databaseSession.commit()                        
                
                except(ValueError, TypeError): 
                    errorMessage = "I'm sorry, I didn't understand the date and time you provided. Please provide your desired appointment time and date in this format (September 18 at 10AM)"
                    return errorMessage

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
                return prompt
        
        #*****************************Confirmation Section**************************************************
        # only create this map when all of the fields of the eventObject are not None [filled out]
        if all(value is not None for value in session.eventObject.values()): 
            # parse the database for the current client confirmation field 
            confirmationField = session.currentConfirmationField

            # return a confirmation message if the user has not seen a confirmation message 
            if session.confirmationShown is None:
                confirmationPrompt = "Is there anything you'd like to change in your appointment details? You can say things like 'change the car model' or 'update the email. If you are done making changes, simply say 'Done'."

                # This returns the message with all of the details parsed from the user and the prompt for the user to make a decision
                return confirmationPrompt + "\n" + displayConfirmationMessage(session.eventObject, session.serviceDuration)
            
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
                    pass
                
                # iterate through the potential fields that the user wants to edit 
                for field, keywords in languageFieldMap.items(): 
                    # if the userInput matches a field to edit 
                    if any(keyword in userInput for keyword in keywords): 
                        # set the current confirmation field and then return the prompt associated with the field 
                        session.currentConfirmationField = field
                        databaseSession.commit()

                        prompt = generatePrompt(field)
                        return prompt
        


    else: 
        # reset if something was made
        if intentObject:
            session.intentObject = None 
            databaseSession.commit()
        response = chatModel.generate_content(userInput).text
        return response