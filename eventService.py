# Loads service account credentials
from google.oauth2.service_account import Credentials
# Creates the connection to one of Google's product API (in our case, Google Calendar)
from googleapiclient.discovery import build 


from dotenv import load_dotenv
import os 
load_dotenv()

def initializeCalendarService(): 
    #* Service account registration
    SCOPES = ['https://www.googleapis.com/auth/calendar']
    creds = Credentials.from_service_account_file(os.getenv('SERVICE_ACCOUNT'), scopes=SCOPES)

    #* Initialize calendar API service
    calendarService = build('calendar', 'v3', credentials=creds)

    return calendarService

#* Specify the calendarId (which calendar) to modify | schedule appointments on 
TARGET_CALENDAR_ID = os.getenv('CALENDAR_ID')

def displayAllEvents(): 
    try: 
        calendarService = initializeCalendarService()
        resultList = calendarService.events().list(calendarId=TARGET_CALENDAR_ID, maxResults=10, singleEvents=True, orderBy='startTime').execute()
        print(f"This is resultList {resultList}")
        eventList = resultList.get('items', [])
        print(f"This is eventList {eventList}")

        if not eventList: 
            print("[displayAllEvents_Try]: No events were found")
        for event in eventList: 
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(f"[displayAllEvents_Try]: Event: {event['summary']}, Start: {start}, ID: {event['id']}")
    
    except: 
        print(f"[displayAllEvents]: There was an error displaying all the events in this calendar.")

# def createEventObject(): 
#     # an Event object must have 
#     # Title | Summary
#     # Location 
#     # Description | Type of wash [interior, exterior, both]
#     # startTime | start
#     # endTime | end 
#     # customer | attendees
#     eventObject = {
#         'summary': '2006 Acura RSX', 
#         'location': 'insert_address_here', 
#         'description': 'Interior & Exterior Cleaning', 
#         'start' : { 
#             'dateTime': '2024-09-02T10:00:00-07:00',
#             'timeZone': 'America/Los_Angeles',
#         }, 
#         'end': { 
#             'dateTime': '2024-09-02T11:00:00-07:00',
#             'timeZone': 'America/Los_Angeles',
#         }, 

#         # 'attendees': [
#         #     {'email': 'attendee1@example.com'},
#         #     {'email': 'attendee2@example.com'},
#         # ],
#     }

#     print("[createEventObject]: Ran successsfully")
#     return eventObject

def createEventObject(carType, location, description, start):
    eventObject = { 
        'summary': carType, 
        'location': location,
        'description': description,
        'start': start,
        'end': start + 1, 
    }

    print("[createEventObject]: Ran successfully")
    return eventObject

#* Adds the event object into company calendar
def addEvent(eventObject): 
    try: 
        calendarService = initializeCalendarService()
        # add the event into the company calendar
        event = calendarService.events().insert(calendarId=TARGET_CALENDAR_ID, body=eventObject).execute()
        print('[addEvent]: Event created- %s' % (event.get('htmlLink')))

    except Exception as e: 
        print(f"[addEvent]: An error occurred-- {e}")

#* Deletes the event object from the company calendar via event_id
def deleteEvent(eventId): 
    try: 
        calendarService = initializeCalendarService()

        # delete the event 
        calendarService.events().delete(calendarId=TARGET_CALENDAR_ID, eventId=eventId).execute()
        print(f"[deleteEvent]: Event with ID {eventId} deleted successfully.")
    
    except Exception as e: 
        print(f"[deleteEvent]: An error occurred-- {e}")

def editEvent(eventId, newStartTime, newEndTime): 
    try: 
        calendarService = initializeCalendarService() 

        # Get the current event details 
        event = calendarService.events().get(calendarId=TARGET_CALENDAR_ID, eventId=eventId).execute()

        # key into the start time of the current event 
        event['start'] = {'dateTime': newStartTime.isoformat(), 'timeZone': 'America/Los_Angeles'}
        event['end'] = {'dateTime': newEndTime.isoformat(), 'timeZone': 'America/Los_Angeles'}

        # update the event details 
        updatedEvent = calendarService.events().update(calendarId=TARGET_CALENDAR_ID, eventId=eventId, body=event).execute()

        print(f"Event updated: {updatedEvent['updated']}")

    except Exception as e: 
        print(f"[editEvent]: An error occurred-- {e}")