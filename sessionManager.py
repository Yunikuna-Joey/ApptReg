# SQLAlchemy Database imports
from sqlalchemy import Column, Integer, String, JSON, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker 
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine

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

    def __repr__(self):
        return f"<UserSession(user_id={self.user_id}, intent_object={self.intent_object})>"
    
def initializeDatabase(engine): 
    Base.metadata.create_all(engine)

#* initialize a current session and database connected to the session-changes
engine = create_engine('sqlite:///sessions.db', echo=True)
Session = sessionmaker(bind=engine)
dbSession = Session()
initializeDatabase(engine)

# Grab a user session
def getUserSession(userId): 
    return dbSession.query(UserSession).filter_by(userId=userId).first()



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