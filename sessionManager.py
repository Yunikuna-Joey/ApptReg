# SQLAlchemy Database imports
from sqlalchemy import Column, Integer, String, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Mock data model 
class UserSession(Base): 
    __tablename__ = 'user_sessions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    userId = Column(String, unique=True, nullable=False)
    instagramUsername = Column(String, unique=True, nullable=False)

    # Fields 
    intentObject = Column(String, nullable=True)
    descriptionObject = Column(String, nullable=True)
    serviceDuration = Column(Integer, nullable=True)
    currentField = Column(String, nullable=True)
    savedStartTime = Column(String, nullable=True)

    eventObject = Column(JSON)

    # Constructor
    def __init__(self, userId, instagramUsername): 
        self.userId = userId
        self.instagramUsername = instagramUsername
        self.intentObject = None
        self.descriptionObject = None
        self.serviceDuration = None
        self.currentField = None
        self.savedStartTime = None
        self.eventObject = {
            'name': None, 
            'number': None, 
            'email': None, 
            'carModel': None, 
            'location': None,
            'description': None,
            'start': None,
        }

    # Create a new user session in the database [Possible override | conflict with constructor class]
    @classmethod
    def createUserSession(cls, userId, sessionData, dbSession): 
        newSession = cls(userId, sessionData)
        dbSession.add(newSession)
        dbSession.commit()
        return newSession

    # Retrieve a user session from the database
    @classmethod
    def getUserSession(cls, userId, dbSession): 
        userSession = dbSession.query(cls).filter_by(userId=userId).first()
        return userSession

    # This creates logs in the terminal to understand what is happening with the database [optional]
    def __repr__(self):
        return f"<UserSession(user_id={self.userId}, intent_object={self.intentObject})>"
    
def initializeDatabase(engine): 
    Base.metadata.create_all(engine)




#********************************Old implementation********************************

# This will be handled in-memory and hold the information about 
#   the user and their following details about their potential appointment 
#   || Going to need a a way to clear the session after a period of inactivity  

# sessionManagement = {} 

# def getUserSession(userId): 
#     """
#     Gets the current user session, if there is not an active one, one will be made
#     """
#     if userId not in sessionManagement: 
#         # intialize the session for the userId 
#         sessionManagement[userId] = { 
#             'intentObject': None, 
#             'eventObject': { 
#                 'name': None, 
#                 'number': None, 
#                 'email': None, 
#                 'carModel': None, 
#                 'location': None, 
#                 'description': None, 
#                 'start': None,
#             }, 
#             'descriptionObject': None, 
#             'serviceOffsetTime': 0,
#             'currentField': None, 
#             'savedStartTime': None
#         } 
    
#     return sessionManagement[userId]

# def updateUserSession(userId, field, sessionData): 
#     """  Updates the user session with the data provided """
#     sessionManagement[userId][field] = sessionData