# This will be handled in-memory and hold the information about 
#   the user and their following details about their potential appointment 
#   || Going to need a a way to clear the session after a period of inactivity  
sessionManagement = {} 

def getUserSession(userId): 
    """
    Gets the current user session, if there is not an active one, one will be made
    """
    if userId not in sessionManagement: 
        # intialize the session for the userId 
        sessionManagement[userId] = { 
            'intentObject': None, 
            'eventObject': { 
                'name': None, 
                'number': None, 
                'email': None, 
                'carModel': None, 
                'location': None, 
                'description': None, 
                'start': None,
            }, 
            'descriptionObject': None, 
            'serviceOffsetTime': 0,
            'currentField': None
        } 
    
    return sessionManagement[userId]

def updateUserSession(userId, sessionData): 
    """  Updates the user session with the data provided """
    sessionManagement[userId] = sessionData