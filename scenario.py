from zoneinfo import ZoneInfo
from sessionManager import getUserSession, updateUserSession
from model import initializeChatModel, initializeClassificationModel
from helper import emailChecker, generatePrompt, phoneNumberChecker, carDescriptionchecker, serviceToHours, serviceTypeChecker
from eventService import checkWeekendCondition, checkDayState, checkWorkHour, listAvailableTimeValidMonth, populateEventsForDay
from dateutil import parser

def additionScenario(userId, userInput): 
    chatModel = initializeChatModel() 
    intentModel = initializeClassificationModel()

    session = getUserSession(userId) 

    # exit conditions 
    if userInput.lower().strip() in ['exit', 'quit', 'stop']: 
        return "Ending the converstaion. Goodbye!"

    intentObject = session['intentObject']
    eventObject = session['eventObject']
    currentField = session['currentField']      # used to maintain session

    if not intentObject: 
        intentObject = intentModel.generate_content(userInput)
        session['intentObject'] = intentObject.text

    print(f"This is the value of intentObject {intentObject.text.lower()}")

    if intentObject.text.lower().strip() in ['create', 'appointment scheduling']: 
        # determine if there is a field in-progress 
        if currentField: 
            # Field validation
            if currentField == 'number': 
                if phoneNumberChecker(userInput) == False:
                    errorMessage = "I apologize, I didn't understand the phone number you provided. Please use the format 999-123-456"
                    return  errorMessage
                
                eventObject['number'] = userInput
                session['currentField'] = None 
            
            elif currentField == 'email': 
                if emailChecker(userInput) == False: 
                    errorMessage = "I'm sorry, I didn't understand the email you entered. Please enter a valid email address that can receive emails."
                    return errorMessage

                eventObject['email'] = userInput
                session['currentField'] = None 
            
            elif currentField == 'carModel': 
                if carDescriptionchecker(userInput) == False: 
                    errorMessage = "I apologize, I didn't understand the car year/make/model that you provided. Please provide your car in the format year/make/model. (Ex: 2015 Honda Civic)"
                    return errorMessage

                eventObject['carModel'] = userInput
                session['currentField'] = None 
            
            elif currentField == 'description': 
                if serviceTypeChecker(userInput) == False: 
                    errorMessage = "That is not a service we offer. Please choose a service we offer: interior, exterior, or both."
                    return errorMessage

                if 'both' in userInput or 'Both' in userInput: 
                    userInput = 'Exterior & Interior'
                    session['serviceOffsetTime'] = serviceToHours(userInput)
                    eventObject['description'] = userInput
                    session['currentField'] == None 
                
                else: 
                    session['serviceOffsetTime'] == serviceToHours(userInput)
                    eventObject['description'] = userInput
                    session['currentField'] == None 
                
            elif currentField == 'start': 
                try: 
                    startTime = parser.parse(userInput)

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
                    
                    listAvailableTimeValidMonth()
                    scheduledEventList = populateEventsForDay(startTime)
                    
                    newStartTime = startTime.astimezone(ZoneInfo("America/Los_Angeles"))

                    # if any(event['start']['dateTime'] == newStartTime.isoformat() for event in scheduledEventList):

                
                except(ValueError, TypeError): 
                    errorMessage = "I'm sorry, I didn't understand the date and time you provided. Please provide your desired appointment time and date in this format (September 18 at 10AM)"
                    return errorMessage
                

        for field, value in eventObject.items(): 
            if value is None: 
                # set the current field for in-memory session management
                session['currentField'] = field

                # generate a prompt for the missing field 
                prompt = generatePrompt(field)
                return prompt

    else: 
        if intentObject:
            intentObject = None
            session['intentObject'] = None
        response = chatModel.generate_content(userInput).text
        return response


