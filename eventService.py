# Loads service account credentials
from google.oauth2.service_account import Credentials
# Creates the connection to one of Google's product API (in our case, Google Calendar)
from googleapiclient.discovery import build 

from datetime import datetime, timedelta, timezone
import pytz

from dotenv import load_dotenv
import os 
load_dotenv()

# constructor for calendar service
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

# Displays all of the events within the current week that the function was invoked
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

#* list all the available timeslots within the work hour [customize to fit]
def listAvailableTime(): 
    try: 
        calendarService = initializeCalendarService()

        # this is a declaration of a datetime object [date & time]
        now = datetime.now(timezone.utc)

        # replacing the day parameter of the datetime object with day number 1 [first of the month]
        startOfMonth = now.replace(day=1)

        # condition to check if we are on december as it requires different logic    
        if startOfMonth.month == 12: 
            # if december, then we make the calculation for the next year january 
            # minus one second to bring us back to the correct last day of december
            endOfMonth = startOfMonth.replace(year=startOfMonth.year + 1, month=1, day=1) - timedelta(seconds=1)
        else:
            endOfMonth = startOfMonth.replace(month=startOfMonth.month + 1, day=1) - timedelta(seconds=1)
        
        # declare our constraints of start day of the month and end day of the month 
        # in isoFormat()
        timeMin = startOfMonth.isoformat()
        timeMax = endOfMonth.isoformat() 

        # this will return a dict object back or dict of dict
        resultList = calendarService.events().list(
            calendarId=TARGET_CALENDAR_ID,
            timeMin=timeMin, 
            timeMax=timeMax,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        # this list just holds all of the event objects within the current constraint
        # the constraint is currently just the entire 1 month of the time of function invoke
        eventList = resultList.get('items', [])

        if not eventList: 
            print("[listAvailableTimes]: There are no events this month")
        
        # (8, 20) signifies the hours from 8AM to 8PM  [24 hour format]
        # workHours = [(8, 20)] 
        availableSlots = {}

        # Iterating through every day of the current month 
        # starting from the first day of the current month
        currDay = startOfMonth
        while currDay <= endOfMonth: 
            # if the current day is a weekend [5, 6] representing 
            # Saturday and Sunday respectively 
            if currDay.weekday() in [5, 6]: 
                #*** we are currently iterating through the eventList of event objects each time, but
                #*** we can make it less taxing by removing the already processed days/event objects
                #*** to improve performance slightly
                weekendObjectList = [
                    # list comprehension to iterate through each event in event list
                    event for event in eventList
                    # the condition to only get the events that match the current day we are iterating on
                    if event['start'].get('dateTime', event['start'].get('date')).startswith(currDay.strftime('%Y-%m-%d'))
                ]

                # create the startTime and endTime
                timeStart = currDay.replace(hour=8, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)
                timeEnd = currDay.replace(hour=20, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)

                # This is essentially representing the company's working hours
                timeAvailable = [(timeStart, timeEnd)]

                # iterating over all the events that happen to land on a weekend
                for event in weekendObjectList: 
                    """ From the event object that we are processing, 
                    process that specific event object's start and end time(s)
                    """
                    eventStart = datetime.fromisoformat(event['start'].get('dateTime').replace("Z", "+00:00"))
                    eventEnd = datetime.fromisoformat(event['end'].get('dateTime').replace("Z", "+00:00"))

                    # split available times around the event
                    newAvailableTimes = []
                    for workStart, workEnd in timeAvailable: 
                        # if event overlaps the available timeslot, split the slot 
                        if eventStart <= workStart < eventEnd or workStart < eventStart < workEnd: 
                            
                            if workStart < eventStart: 
                                newAvailableTimes.append((workStart, eventStart))
                            
                            if eventEnd < workEnd: 
                                newAvailableTimes.append((eventEnd, workEnd))
                            
                        else: 
                            # print(f"This is workStart and workEnd {workStart} {workEnd}")
                            newAvailableTimes.append((workStart, workEnd))
                            

                    timeAvailable = newAvailableTimes
                
                availableSlots[currDay.strftime('%Y-%m-%d')] = timeAvailable
            
            # move to the next day
            currDay += timedelta(days=1)

        for date, times in availableSlots.items(): 
            if times: 
                print(f"Available times on {date}:")
                for start, end in times: 
                    print(f" {start.strftime('%I:%M %p')} - {end.strftime('%I:%M %p')}")
                print('\n')
            
            else: 
                print(f"No available times on {date}")

    except Exception as e: 
        print(f"[listAvailableTimes]: There was an error displaying the available weekend times {e}") 

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