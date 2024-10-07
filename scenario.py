from sessionManager import getUserSession, updateUserSession
from model import initializeChatModel, initializeClassificationModel
from helper import generatePrompt

def additionScenario(userId, userInput): 
    chatModel = initializeChatModel() 
    intentModel = initializeClassificationModel()

    session = getUserSession(userId) 

    # exit conditions 
    if userInput.lower().strip() in ['exit', 'quit', 'stop']: 
        return "Ending the converstaion. Goodbye!"

    intentObject = session['intentObject']
    eventObject = session['eventObject']

    if not intentObject: 
        intentObject = intentModel.generate_content(userInput)
        session['intentObject'] = intentObject
    
    if intentObject.text.lower().strip() in ['create', 'appointment scheduling']: 
        for field, value in eventObject.items(): 
            if value is None: 
                # generate a prompt for the missing field 
                prompt = generatePrompt(field)
                return prompt

    else: 
        response = chatModel.generate_content(userInput)
        return response

                

