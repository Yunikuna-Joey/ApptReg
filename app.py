from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build 

from dotenv import load_dotenv
import os 
import google.generativeai as genai

load_dotenv()

#* Global registration variables 
apiKey = os.getenv('API_TOKEN')
genai.configure(api_key=apiKey)
model = genai.GenerativeModel(os.getenv('API_MODEL'))

#* Service account registration
SCOPES = ['https://www.googleapis.com/auth/calendar']
creds = Credentials.from_service_account_file(os.getenv('SERVICE_ACCOUNT'), scopes=SCOPES)

#* Initialize calendar API service
calendarService = build('calendar', 'v3', credentials=creds)

#* Specify the calendarId (which calendar) to modify | schedule appointments on 
targetCalendarId = os.getenv('CALENDAR_ID')

#* Example of creating an event on the company calendar 
    # an Event object must have 
    # Title | Summary
    # Location 
    # Description | Type of wash [interior, exterior, both]
    # startTime | start
    # endTime | end 
    # customer | attendees
eventObject = {
    'summary': 'Company Meeting', 
    'location': 'Office', 
    'description': 'Discussing project updates', 
    'start' : { 
        'dateTime': '2024-09-01T10:00:00-07:00',
        'timeZone': 'America/Los_Angeles',
    }, 
    'end': { 
        'dateTime': '2024-09-01T11:00:00-07:00',
        'timeZone': 'America/Los_Angeles',
    }, 
    # 'attendees': [
    #     {'email': 'attendee1@example.com'},
    #     {'email': 'attendee2@example.com'},
    # ],
}

#* Insert the event into the company calendar
# event = calendarService.events().insert(calendarId=targetCalendarId, body=eventObject).execute()
# print('Event created: %s' % (event.get('htmlLink')))


#* Example request [refer back as necessary]
def exampleClientRequest():
    response = model.generate_content("What is the most popular food?")
    print(response.text)

def example(): 
    response = model.generate_content("Hello, I would like to schedule an appointment")
    print(response.text)

if __name__ == "__main__": 
    #* Insert the event into the company calendar
    event = calendarService.events().insert(calendarId=targetCalendarId, body=eventObject).execute()
    print('Event created: %s' % (event.get('htmlLink')))

