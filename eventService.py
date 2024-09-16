# Loads service account credentials
from google.oauth2.service_account import Credentials
# Creates the connection to one of Google's product API (in our case, Google Calendar)
from googleapiclient.discovery import build 

from datetime import datetime, timedelta
import pytz

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

#* potentially necessary for determining eventID 
def displayAllEvents(): 
    try: 
        calendarService = initializeCalendarService()
        resultList = calendarService.events().list(calendarId=TARGET_CALENDAR_ID, maxResults=10, singleEvents=True, orderBy='startTime').execute()
        # print(f"This is resultList {resultList}")
        eventList = resultList.get('items', [])
        print(f"This is eventList {eventList}")

        if not eventList: 
            print("[displayAllEvents_Try]: No events were found")
        for event in eventList: 
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(f"[displayAllEvents_Try]: Event: {event['summary']}, Start: {start}, ID: {event['id']}")
    
    except: 
        print(f"[displayAllEvents]: There was an error displaying all the events in this calendar.")

def displayCurrWeekEvents():
    try: 
        # Initialize the Calendar Service
        calendarService = initializeCalendarService()
        
        # current time of function invoke
        now = datetime.now()

        # determine the start of week [day] and end of week [day]
        start_of_week = now - timedelta(days=now.weekday())  # Monday
        end_of_week = start_of_week + timedelta(days=6, hours=23, minutes=59)  # Sunday, end of day

        # Convert to ISO format for the API
        timeMin = start_of_week.isoformat() + 'Z'  # Z indicates UTC time
        timeMax = end_of_week.isoformat() + 'Z'

        # create list with desired parameters
        resultList = calendarService.events().list(
            calendarId=TARGET_CALENDAR_ID,
            timeMin=timeMin,
            timeMax=timeMax,
            maxResults=10,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        eventList = resultList.get('items', [])
        
        if not eventList: 
            print("[displayWeekEvents]: No events found for this week.")
        
        # Display the events
        for event in eventList: 
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(f"[displayWeekEvents]: Event: {event['summary']}, Start: {start}, ID: {event['id']}")
    
    except Exception as e: 
        print(f"[displayWeekEvents]: There was an error displaying the events for the week: {e}")

# grabs all of the weekend events within a current month
def displayWeekendEvents():
    try:
        # Initialize the Calendar Service
        calendarService = initializeCalendarService()

        now = datetime.now()
        # print(f"this is the value of now {now}")

        # find the first day of current month and last day of current month
        start_of_month = now.replace(day=1)  # First day of the month
        # print(f"this is start of month {start_of_month}")

        # Calculate the first day of the next month, then subtract 1 second to get the last day of this month
        end_of_month = (start_of_month.replace(month=start_of_month.month % 12 + 1, day=1) - timedelta(seconds=1))
        # print(f"this is end of month {end_of_month}")

        # Convert to ISO format for the API with timezone information
        timeMin = start_of_month.isoformat() + 'Z'
        timeMax = end_of_month.isoformat() + 'Z'

        # populate the list 
        resultList = calendarService.events().list(
            calendarId=TARGET_CALENDAR_ID,
            timeMin=timeMin,
            timeMax=timeMax,
            maxResults=100,  # Fetch more events to cover the entire month
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        eventList = resultList.get('items', [])
        
        if not eventList:
            print("[displayWeekendEvents]: No events found for this month.")

        # Display only weekend events (Saturday and Sunday)
        for event in eventList:
            # Get the event's start time as a datetime object
            start = event['start'].get('dateTime', event['start'].get('date'))
            event_start_datetime = datetime.fromisoformat(start)

            # Check if the event falls on a weekend (Saturday = 5, Sunday = 6)
            if event_start_datetime.weekday() in [5, 6]:
                print(f"[displayWeekendEvents]: Event: {event['summary']}, Start: {start}, ID: {event['id']}")
    
    except Exception as e:
        print(f"[displayWeekendEvents]: There was an error displaying the weekend events: {e}")

#* need a time constraint to only display the available times *this* week  
def populateEventList(): 
    try: 
        calendarService = initializeCalendarService() 
        resultList = calendarService.events().list(calendarId=TARGET_CALENDAR_ID, maxResults=10, singleEvents=True, orderBy='startTime').execute()
        eventList = resultList.get('items', [])

        if not eventList: 
            print("All timeslots are available")
        
        for event in eventList: 
            start = event['start'].get('dateTime', event['start'].get('date'))
            print(f"[displayAllEvents_Try]: Event: {event['summary']}, Start: {start}, ID: {event['id']}")

    
    except: 
        print(f"[populateEventList]: There was an error with gathering the list of all events in the calendar")

def createEventObjectExample(): 
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
            'dateTime': '2024-09-22T10:00:00-07:00',
            'timeZone': 'America/Los_Angeles',
        }, 
        'end': { 
            'dateTime': '2024-09-22T11:00:00-07:00',
            'timeZone': 'America/Los_Angeles',
        }, 

        # 'attendees': [
        #     {'email': 'attendee1@example.com'},
        #     {'email': 'attendee2@example.com'},
        # ],
    }

    print("[createEventObject]: Ran successsfully")
    return eventObject
    
def createEventObject(carType, location, description, start):
    print(f'This is start time in isoformat {start.isoformat()}')
    eventObject = { 
        'summary': carType, 
        'location': location,
        'description': description,
        'start': {
            'dateTime': start.isoformat(), 
            'timeZone': 'America/Los_Angeles',
        },
        'end': {
            'dateTime': (start + timedelta(hours=1)).isoformat(),
            'timeZone': 'America/Los_Angeles', 
        }
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