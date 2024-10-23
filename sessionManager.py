# SQLAlchemy Database imports
from sqlalchemy import Column, Integer, String, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.types import TypeDecorator

import json 
import datetime

Base = declarative_base()

class JSONEncodeDict(TypeDecorator): 
    impl = JSON 

    # serializing the start time from datetime object into isoformat 
    def process_bind_param(self, value, dialect):
        if value is None: 
            return None 
        
        def serialize(object): 
            if isinstance(object, datetime.datetime):
                return object.isoformat()

            return object 
    
        return json.dumps(value, default=serialize)
    
    def process_result_value(self, value, dialect):
        if value is None: 
            return None 
        
        # convert string back to datetime objects
        def datetimeParse(dictObject): 
            for key, val in dictObject.items(): 
                try: 
                    dictObject[key] = datetime.datetime.fromisoformat(val)
                
                except (ValueError, TypeError): 
                    continue
            
            return dictObject
        
        return json.loads(value, object_hook=datetimeParse)

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
    confirmationCode = Column(String, nullable=True)
    confirmationShown = Column(Boolean, nullable=True)
    currentConfirmationField = Column(String, nullable=True)

    eventObject = Column(MutableDict.as_mutable(JSONEncodeDict))

    # Constructor
    def __init__(self, userId, instagramUsername): 
        self.userId = userId
        self.instagramUsername = instagramUsername
        self.intentObject = None
        self.descriptionObject = None
        self.serviceDuration = None
        self.currentField = None
        self.confirmationCode = None 
        self.confirmationShown = None
        self.currentConfirmationField = None
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