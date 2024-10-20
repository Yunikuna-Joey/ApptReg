# SQLAlchemy Database imports
from sqlalchemy import Column, Integer, String, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Mock data model 
class UserSession(Base): 
    __tablename__ = 'user_sessions'

    id = Column(Integer, primary_key=True, autoincrement=True)
    userId = Column(String, unique=True, nullable=False)

    # Fields 
    intentObject = Column(String, nullable=True)
    descriptionObject = Column(String, nullable=True)
    serviceDuration = Column(Integer, default=0)
    currentField = Column(String, nullable=False)
    savedStartTime = Column(String, nullable=False)

    eventObject = Column(JSON)

    # Constructor
    def __init__(self, userId, sessionData): 
        self.userId = userId
        self.intentObject = sessionData['intentObject']
        self.descriptionObject = sessionData['descriptionObject']
        self.serviceDuration = sessionData['serviceDuration']
        self.currentField = sessionData['currentField']
        self.savedStartTime = sessionData['savedStartTime']
        self.eventObject = sessionData['eventObject']

    # Create a new user session in the database
    @classmethod
    def createUserSession(cls, userId, sessionData, dbSession): 
        newSession = cls(userId, sessionData)
        dbSession.add(newSession)
        dbSession.commit()
        return newSession

    # Retrieve a user session from the database
    @classmethod
    def getUserSession(cls, userId, dbSession): 
        return dbSession.query(cls).filter_by(userId=userId).first()

    def __repr__(self):
        return f"<UserSession(user_id={self.user_id}, intent_object={self.intent_object})>"
    
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