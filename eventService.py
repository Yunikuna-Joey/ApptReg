# Loads service account credentials
from google.oauth2.service_account import Credentials
# Creates the connection to one of Google's product API (in our case, Google Calendar)
from googleapiclient.discovery import build 

from dotenv import load_dotenv
import os 
load_dotenv()

#* Service account registration
SCOPES = ['https://www.googleapis.com/auth/calendar']
creds = Credentials.from_service_account_file(os.getenv('SERVICE_ACCOUNT'), scopes=SCOPES)

#* Initialize calendar API service
calendarService = build('calendar', 'v3', credentials=creds)

#* Specify the calendarId (which calendar) to modify | schedule appointments on 
targetCalendarId = os.getenv('CALENDAR_ID')

def createEventObject(): 
    # an Event object must have 
    # Title | Summary
    # Location 
    # Description | Type of wash [interior, exterior, both]
    # startTime | start
    # endTime | end 
    # customer | attendees
    eventObject = {
        'summary': '2006 Acura RSX', 
        'location': 'insert_address_here', 
        'description': 'Interior & Exterior Cleaning', 
        'start' : { 
            'dateTime': '2024-09-02T10:00:00-07:00',
            'timeZone': 'America/Los_Angeles',
        }, 
        'end': { 
            'dateTime': '2024-09-02T11:00:00-07:00',
            'timeZone': 'America/Los_Angeles',
        }, 

        # 'attendees': [
        #     {'email': 'attendee1@example.com'},
        #     {'email': 'attendee2@example.com'},
        # ],
    }

    print("[createEventObject]: Ran successsfully")
    return eventObject

#* Adds the event object into company calendar
def addEvent(eventObject): 
    event = calendarService.events().insert(calendarId=targetCalendarId, body=eventObject).execute()
    print('[addEvent]: Event created- %s' % (event.get('htmlLink')))