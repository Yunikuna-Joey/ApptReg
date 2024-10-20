# Utility imoprts
from zoneinfo import ZoneInfo
from dateutil import parser

# Helper file imports
from model import initializeChatModel, initializeClassificationModel
from helper import emailChecker, generatePrompt, phoneNumberChecker, carDescriptionchecker, serviceToHours, serviceTypeChecker
from eventService import checkWeekendCondition, checkDayState, checkWorkHour, populateAvailableTimesMonth, populateEventsForDay

# database import 
from sessionManager import UserSession

def additionScenario(userId, userInput, databaseSession): 
    # intialize the chat model
    chatModel = initializeChatModel()  

    # grab the current user session
    session = UserSession.getUserSession(userId, databaseSession)

    if session is None: 
        # constructor class being called for default values associated with instagramUID
        session = UserSession(userId)

    # debugging statement 
    print(f"This is the value of current user session {session}")

    # exit conditions 
    if userInput.lower().strip() in ['exit', 'quit', 'stop']: 
        return "Ending the converstaion. Goodbye!"

    # initialize variables to current user session
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
    #* This is the possible source of error 
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
                session.eventObject['number'] = userInput
                session.currentField = None 
                databaseSession.commit()                                
            
            elif currentField == 'email': 
                # Error checking with function
                if emailChecker(userInput) == False: 
                    errorMessage = "I'm sorry, I didn't understand the email you entered. Please enter a valid email address that can receive emails."
                    return errorMessage

                # Commit changes into the database
                session.eventObject['email'] = userInput
                session.currentField['currentField'] = None 
                databaseSession.commit()
            
            elif currentField == 'carModel': 
                # Error checking 
                if carDescriptionchecker(userInput) == False: 
                    errorMessage = "I apologize, I didn't understand the car year/make/model that you provided. Please provide your car in the format year/make/model. (Ex: 2015 Honda Civic)"
                    return errorMessage

                # Commit changes into the database 
                session.eventObject['carModel'] = userInput 
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
                    session.eventObject['description'] = userInput
                    session.currentField = None
                    databaseSession.commit()
                
                else: 
                    session.serviceDuration = serviceToHours(userInput)
                    session.eventObject['description'] = userInput
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
                    session.eventObject['start'] = startTime
                    databaseSession.commit()                        
                
                except(ValueError, TypeError): 
                    errorMessage = "I'm sorry, I didn't understand the date and time you provided. Please provide your desired appointment time and date in this format (September 18 at 10AM)"
                    return errorMessage

            else: 
                if 'facility' in userInput and field == 'location': 
                    userInput = 'Onsite Appointment'
                
                session.eventObject[field] = userInput
                databaseSession.commit()

        # Iterate through the user session's event object
        for field, value in session.eventObject.items(): 
            if value is None: 
                # set the current field for database session management
                session.currentField = field 
                databaseSession.commit()

                # generate a prompt for the missing field 
                prompt = generatePrompt(field)
                return prompt

    else: 
        # reset if something was made
        if intentObject:
            session.intentObject = None 
            databaseSession.commit()
        response = chatModel.generate_content(userInput).text
        return response