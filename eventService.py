# Loads service account credentials
from google.oauth2.service_account import Credentials
# Creates the connection to one of Google's product API (in our case, Google Calendar)
from googleapiclient.discovery import build 

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from dotenv import load_dotenv
import os

from helper import convertDateTime 
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
def listAvailableTimeExample(): 
    try: 
        calendarService = initializeCalendarService()

        # this is a declaration of a datetime object [date & time]
        now = datetime.now(timezone.utc)
        print(f"This is the value of now {now}")

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
                        # If event starts before the workEnd and ends after the workStart, it overlaps
                        if eventStart <= workEnd and eventEnd >= workStart: 
                            # If the event starts after the workStart, keep the time before the event
                            if workStart < eventStart: 
                                #* the timedelta here should be replaced with the type of cleaning [interior/exterior = 1hr, both = 2hr]
                                newAvailableTimes.append((workStart, (eventStart - timedelta(hours=1) )))
                            
                            # If the event ends before the workEnd, keep the time after the event
                            if eventEnd < workEnd: 
                                newAvailableTimes.append((eventEnd, workEnd))
                        else: 
                            # No overlap, so keep the original time slot
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
                print(f"No available times on {date}\n")

    except Exception as e: 
        print(f"[listAvailableTimes]: There was an error displaying the available weekend times {e}") 

#* This will ist all the available times within the month and after the current day
def listAvailableTimeValidMonth(): 
    try: 
        calendarService = initializeCalendarService()

        # Set the timezone to 'America/Los_Angeles'
        tz_los_angeles = ZoneInfo('America/Los_Angeles')

        # replacing the current datetime object with information of timezone and setting the time be 1AM [doesn't have to be 1am just some arbitary time that is before the working hours]
        currentDayObject = datetime.now(tz=tz_los_angeles).replace(hour=1, minute=0, second=0, microsecond=0)
        print(f"Value of currentDayobject {currentDayObject}")
        
        # # Print the dateTimeObject with the assigned timezone for debugging
        # print(f"[listAvailableTime]: {currentDayObject}")
        startThreshhold = currentDayObject


        if startThreshhold.month == 12: 
            endOfMonth = startThreshhold.replace(year=startThreshhold.year + 1, month=1, day=1) - timedelta(seconds=1)
        else:
            endOfMonth = startThreshhold.replace(month=startThreshhold.month + 1, day=1) - timedelta(seconds=1)
        
        
        # declare our constraints of start day of the month and end day of the month 
        # in isoFormat()
        timeMin = startThreshhold.isoformat()
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
            print("[listAvailableTime]: There are no events this month")
        
        # (8, 20) signifies the hours from 8AM to 8PM  [24 hour format]
        # workHours = [(8, 20)] 
        availableSlots = {}

        # Iterating through every day of the current month 
        # starting from the first day of the current month
        currDay = startThreshhold
        weekendsFound = False 

        while currDay <= endOfMonth: 
            # if the current day is a weekend [5, 6] representing 
            # Saturday and Sunday respectively 
            if currDay.weekday() in [5, 6]: 
                weekendsFound = True 

                #*** we are currently iterating through the eventList of event objects each time, but
                #*** we can make it less taxing by removing the already processed days/event objects
                #*** to improve performance slightly
                weekendObjectList = [
                    # list comprehension to iterate through each event in event list
                    event for event in eventList
                    # the condition to only get the events that match the current day we are iterating on
                    if event['start'].get('dateTime', event['start'].get('date')).startswith(currDay.strftime('%Y-%m-%d'))
                ]

                # print(f"[listAvailableTimeValidMonth L:312]: This is the weekendObjectList value {weekendObjectList}")

                # create the startTime and endTime
                # timeStart = currentDayObject.replace(hour=8, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)
                # timeEnd = currentDayObject.replace(hour=20, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)
                timeStart = currDay.replace(hour=8, minute=0, second=0, microsecond=0)
                timeEnd = currDay.replace(hour=20, minute=0, second=0, microsecond=0)

                # This is essentially representing the company's working hours
                timeAvailable = [(timeStart, timeEnd)]

                # iterating over all the events that happen to land on a weekend
                for event in weekendObjectList: 
                    """ From the event object that we are processing, 
                    process that specific event object's start and end time(s)
                    """
                    # eventStart = datetime.fromisoformat(event['start'].get('dateTime').replace("Z", "+00:00"))
                    # eventEnd = datetime.fromisoformat(event['end'].get('dateTime').replace("Z", "+00:00"))
                    eventStart = datetime.fromisoformat(event['start'].get('dateTime'))
                    eventEnd = datetime.fromisoformat(event['end'].get('dateTime'))

                    # split available times around the event
                    newAvailableTimes = []
                    for workStart, workEnd in timeAvailable: 
                        # If event starts before the workEnd and ends after the workStart, it overlaps
                        if eventStart <= workEnd and eventEnd >= workStart: 
                            # If the event starts after the workStart, keep the time before the event
                            if workStart < eventStart: 
                                #* the timedelta here should be replaced with the type of cleaning [interior/exterior = 1hr, both = 2hr]
                                # newAvailableTimes.append((workStart, (eventStart - timedelta(hours=1) )))
                                newAvailableTimes.append((workStart, eventStart))
                            
                            # If the event ends before the workEnd, keep the time after the event
                            if eventEnd < workEnd: 
                                newAvailableTimes.append((eventEnd, workEnd))
                        else: 
                            # No overlap, so keep the original time slot
                            newAvailableTimes.append((workStart, workEnd))
                            
                    timeAvailable = newAvailableTimes
                    
                availableSlots[currDay.strftime('%Y-%m-%d')] = timeAvailable
            
            # move to the next day
            currDay += timedelta(days=1)

        if not weekendsFound: 
            print("[Teni]: No weekends were found this month, checking the next month...")
            nextMonth = startThreshhold.replace(day=1)
            if nextMonth.month == 12:
                nextMonth = nextMonth.replace(year=nextMonth.year + 1, month=1)
            else:
                nextMonth = nextMonth.replace(month=nextMonth.month + 1)

            nextMonthEnd = nextMonth.replace(day=1).replace(month=nextMonth.month + 1) - timedelta(seconds=1)

            timeMinNextMonth = nextMonth.isoformat()
            timeMaxNextMonth = nextMonthEnd.isoformat()

            # Query events for the next month
            resultListNextMonth = calendarService.events().list(
                calendarId=TARGET_CALENDAR_ID,
                timeMin=timeMinNextMonth,
                timeMax=timeMaxNextMonth,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            eventListNextMonth = resultListNextMonth.get('items', [])

            # Process weekends in the next month (similar logic to current month)
            currDay = nextMonth
            while currDay <= nextMonthEnd:
                if currDay.weekday() in [5, 6]:
                    weekendObjectList = [
                        event for event in eventListNextMonth
                        if event['start'].get('dateTime', event['start'].get('date')).startswith(currDay.strftime('%Y-%m-%d'))
                    ]

                    timeStart = currDay.replace(hour=8, minute=0, second=0, microsecond=0)
                    timeEnd = currDay.replace(hour=20, minute=0, second=0, microsecond=0)
                    timeAvailable = [(timeStart, timeEnd)]

                    for event in weekendObjectList: 
                        eventStart = datetime.fromisoformat(event['start'].get('dateTime'))
                        eventEnd = datetime.fromisoformat(event['end'].get('dateTime'))

                        newAvailableTimes = []
                        for workStart, workEnd in timeAvailable: 
                            if eventStart <= workEnd and eventEnd >= workStart: 
                                if workStart < eventStart: 
                                    newAvailableTimes.append((workStart, eventStart))
                                if eventEnd < workEnd: 
                                    newAvailableTimes.append((eventEnd, workEnd))
                            else: 
                                newAvailableTimes.append((workStart, workEnd))

                        timeAvailable = newAvailableTimes

                    availableSlots[currDay.strftime('%Y-%m-%d')] = timeAvailable
                
                currDay += timedelta(days=1)
    
        for date, times in availableSlots.items(): 
            if times: 
                print(f"Available times on {date}:")
                for start, end in times: 
                    print(f" {start.strftime('%I:%M %p')} - {end.strftime('%I:%M %p')}")
                print('\n')
            
            else: 
                print(f"No available times on {date}\n")
        
    except Exception as e: 
        print(f"[listAvailableTimeValidMonth]: There was an error displaying the available weekend times {e}") 

#* Adapted version for webhook responses [async]
def populateAvailableTimesMonth(): 
    try: 
        calendarService = initializeCalendarService()

        # Set the timezone to 'America/Los_Angeles'
        tz_los_angeles = ZoneInfo('America/Los_Angeles')

        # replacing the current datetime object with information of timezone and setting the time be 1AM [doesn't have to be 1am just some arbitary time that is before the working hours]
        currentDayObject = datetime.now(tz=tz_los_angeles).replace(hour=1, minute=0, second=0, microsecond=0)
        print(f"Value of currentDayobject {currentDayObject}")
        
        # # Print the dateTimeObject with the assigned timezone for debugging
        # print(f"[listAvailableTime]: {currentDayObject}")
        startThreshhold = currentDayObject


        if startThreshhold.month == 12: 
            endOfMonth = startThreshhold.replace(year=startThreshhold.year + 1, month=1, day=1) - timedelta(seconds=1)
        else:
            endOfMonth = startThreshhold.replace(month=startThreshhold.month + 1, day=1) - timedelta(seconds=1)
        
        
        # declare our constraints of start day of the month and end day of the month 
        # in isoFormat()
        timeMin = startThreshhold.isoformat()
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
            print("[listAvailableTime]: There are no events this month")
        
        # (8, 20) signifies the hours from 8AM to 8PM  [24 hour format]
        # workHours = [(8, 20)] 
        availableSlots = {}

        # Iterating through every day of the current month 
        # starting from the first day of the current month
        currDay = startThreshhold
        weekendsFound = False 

        while currDay <= endOfMonth: 
            # if the current day is a weekend [5, 6] representing 
            # Saturday and Sunday respectively 
            if currDay.weekday() in [5, 6]: 
                weekendsFound = True 

                #*** we are currently iterating through the eventList of event objects each time, but
                #*** we can make it less taxing by removing the already processed days/event objects
                #*** to improve performance slightly
                weekendObjectList = [
                    # list comprehension to iterate through each event in event list
                    event for event in eventList
                    # the condition to only get the events that match the current day we are iterating on
                    if event['start'].get('dateTime', event['start'].get('date')).startswith(currDay.strftime('%Y-%m-%d'))
                ]

                # print(f"[listAvailableTimeValidMonth L:312]: This is the weekendObjectList value {weekendObjectList}")

                # create the startTime and endTime
                # timeStart = currentDayObject.replace(hour=8, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)
                # timeEnd = currentDayObject.replace(hour=20, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)
                timeStart = currDay.replace(hour=8, minute=0, second=0, microsecond=0)
                timeEnd = currDay.replace(hour=20, minute=0, second=0, microsecond=0)

                # This is essentially representing the company's working hours
                timeAvailable = [(timeStart, timeEnd)]

                # iterating over all the events that happen to land on a weekend
                for event in weekendObjectList: 
                    """ From the event object that we are processing, 
                    process that specific event object's start and end time(s)
                    """
                    # eventStart = datetime.fromisoformat(event['start'].get('dateTime').replace("Z", "+00:00"))
                    # eventEnd = datetime.fromisoformat(event['end'].get('dateTime').replace("Z", "+00:00"))
                    eventStart = datetime.fromisoformat(event['start'].get('dateTime'))
                    eventEnd = datetime.fromisoformat(event['end'].get('dateTime'))

                    # split available times around the event
                    newAvailableTimes = []
                    for workStart, workEnd in timeAvailable: 
                        # If event starts before the workEnd and ends after the workStart, it overlaps
                        if eventStart <= workEnd and eventEnd >= workStart: 
                            # If the event starts after the workStart, keep the time before the event
                            if workStart < eventStart: 
                                #* the timedelta here should be replaced with the type of cleaning [interior/exterior = 1hr, both = 2hr]
                                # newAvailableTimes.append((workStart, (eventStart - timedelta(hours=1) )))
                                newAvailableTimes.append((workStart, eventStart))
                            
                            # If the event ends before the workEnd, keep the time after the event
                            if eventEnd < workEnd: 
                                newAvailableTimes.append((eventEnd, workEnd))
                        else: 
                            # No overlap, so keep the original time slot
                            newAvailableTimes.append((workStart, workEnd))
                            
                    timeAvailable = newAvailableTimes
                    
                availableSlots[currDay.strftime('%Y-%m-%d')] = timeAvailable
            
            # move to the next day
            currDay += timedelta(days=1)

        if not weekendsFound: 
            print("No weekends were found this month, checking the next month...")
            nextMonth = startThreshhold.replace(day=1)
            if nextMonth.month == 12:
                nextMonth = nextMonth.replace(year=nextMonth.year + 1, month=1)
            else:
                nextMonth = nextMonth.replace(month=nextMonth.month + 1)

            nextMonthEnd = nextMonth.replace(day=1).replace(month=nextMonth.month + 1) - timedelta(seconds=1)

            timeMinNextMonth = nextMonth.isoformat()
            timeMaxNextMonth = nextMonthEnd.isoformat()

            # Query events for the next month
            resultListNextMonth = calendarService.events().list(
                calendarId=TARGET_CALENDAR_ID,
                timeMin=timeMinNextMonth,
                timeMax=timeMaxNextMonth,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            eventListNextMonth = resultListNextMonth.get('items', [])

            # Process weekends in the next month (similar logic to current month)
            currDay = nextMonth
            while currDay <= nextMonthEnd:
                if currDay.weekday() in [5, 6]:
                    weekendObjectList = [
                        event for event in eventListNextMonth
                        if event['start'].get('dateTime', event['start'].get('date')).startswith(currDay.strftime('%Y-%m-%d'))
                    ]

                    timeStart = currDay.replace(hour=8, minute=0, second=0, microsecond=0)
                    timeEnd = currDay.replace(hour=20, minute=0, second=0, microsecond=0)
                    timeAvailable = [(timeStart, timeEnd)]

                    for event in weekendObjectList: 
                        eventStart = datetime.fromisoformat(event['start'].get('dateTime'))
                        eventEnd = datetime.fromisoformat(event['end'].get('dateTime'))

                        newAvailableTimes = []
                        for workStart, workEnd in timeAvailable: 
                            if eventStart <= workEnd and eventEnd >= workStart: 
                                if workStart < eventStart: 
                                    newAvailableTimes.append((workStart, eventStart))
                                if eventEnd < workEnd: 
                                    newAvailableTimes.append((eventEnd, workEnd))
                            else: 
                                newAvailableTimes.append((workStart, workEnd))

                        timeAvailable = newAvailableTimes

                    availableSlots[currDay.strftime('%Y-%m-%d')] = timeAvailable
                
                currDay += timedelta(days=1)
    
        finalList = ""
        for date, times in availableSlots.items(): 
            if times: 
                finalList += f"Available times on {date}:"
                for start, end in times: 
                    finalList += f" {start.strftime('%I:%M %p')} - {end.strftime('%I:%M %p')}\n"
                finalList += '\n'

            else:
                finalList += f"No available times on {date}\n" 

        # This is a string list with the available times 
        return finalList
        
    except Exception as e: 
        print(f"[populateAvailableTimeMonth]: There was an error displaying the available weekend times {e}")

#* This will list all the available times for the entire month
def listAvailableTimeMonth(dateTimeObject): 
    try: 
        calendarService = initializeCalendarService()

        # Set the timezone to 'America/Los_Angeles'
        tz_los_angeles = ZoneInfo('America/Los_Angeles')
        
        # Print the dateTimeObject with the assigned timezone for debugging
        print(f"[listAvailableTime]: {dateTimeObject}")

        # Set the dateTimeObject to 'America/Los_Angeles' if it's naive (no timezone info)
        if dateTimeObject.tzinfo is None:
            dateTimeObject = dateTimeObject.replace(tzinfo=tz_los_angeles)
        else:
            # Convert to 'America/Los_Angeles' if already has tzinfo
            dateTimeObject = dateTimeObject.astimezone(tz_los_angeles)

        # Create the start of the month based on the dateTimeObject
        startOfMonth = dateTimeObject.replace(day=1)

        if startOfMonth.month == 12: 
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
            print("[listAvailableTime]: There are no events this month")
        
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
                        # If event starts before the workEnd and ends after the workStart, it overlaps
                        if eventStart <= workEnd and eventEnd >= workStart: 
                            # If the event starts after the workStart, keep the time before the event
                            if workStart < eventStart: 
                                #* the timedelta here should be replaced with the type of cleaning [interior/exterior = 1hr, both = 2hr]
                                newAvailableTimes.append((workStart, (eventStart - timedelta(hours=1) )))
                            
                            # If the event ends before the workEnd, keep the time after the event
                            if eventEnd < workEnd: 
                                newAvailableTimes.append((eventEnd, workEnd))
                        else: 
                            # No overlap, so keep the original time slot
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
                print(f"No available times on {date}\n")
    
    except Exception as e: 
        print(f"[listAvailableTime]: There was an error displaying the available weekend times {e}") 

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
    
def createEventObject(carType, location, description, start, duration):
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
            'dateTime': (start + timedelta(hours=duration)).isoformat(),
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

        return event
    
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

# publish backend update for the startTime
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

# Allows for the user to change their phone number on record
def editNumber(eventId, number): 
    """
    Takes in the eventId [confirmation code] & the NEW phone number
    """

    try: 
        calendarService = initializeCalendarService()

        # get the current event details 
        event = calendarService.events().get(calendarId=TARGET_CALENDAR_ID, eventId=eventId).execute()

        # the description key has 4 points of information [serviceType, carModel, number, email]
        splitList = event['description'].split('\n')

        # it will always follow the same pattern so we can go straight to the index 
        splitList[1] = number

        finalDescription = '\n'.join(splitList)            # put the list back together 

        event['description'] = finalDescription

        updatedEventObject = calendarService.events().update(calendarId=TARGET_CALENDAR_ID, eventId=eventId, body=event).execute()

        print(f"Successfully updated event: {updatedEventObject.get('htmlLink')}")

    except Exception as e: 
        print(f"[editNumber]: There was an issue changing the number associated with this appointment {e}")

def editSummary(eventId, nameChange): 
    """
    Changes the summary field of a eventObject pulled from a Google Calendar 
    """
    try: 
        calendarService = initializeCalendarService()
        event = calendarService.events().get(calendarId=TARGET_CALENDAR_ID, eventId=eventId).execute()

        # this will update the Summary for the event from Google Calendar
        event['summary'] = nameChange

        updatedEventObject = calendarService.events().update(calendarId=TARGET_CALENDAR_ID, eventId=eventId, body=event).execute()
        print(f"[editSummary]: Successfully changed the summary for the appointment {updatedEventObject['htmlLink']}")

    except Exception as e: 
        print(f"[editSummary]: There was an issue changing the summary for this appointment {e}")

def editLocation(eventId, locationChange): 
    """
    Changes the location field of an eventObject pulled from a Google Calendar 
    """
    try: 
        calendarService = initializeCalendarService()
        event = calendarService.events().get(calendarId=TARGET_CALENDAR_ID, eventId=eventId).execute()

        event['location'] = locationChange 

        updatedEventObject = calendarService.events().update(calendarId=TARGET_CALENDAR_ID, eventId=eventId, body=event).execute()
        print(f"[editLocation]: Successfully changed the location for the appointment {updatedEventObject['htmlLink']}")

    except Exception as e: 
        print(f"[editLocation]: There was an issue changing the location for this appointment {e}")

# allows for the user to change their email address on record
def editEmail(eventId, emailAddress): 
    try: 
        calendarService = initializeCalendarService()

        # grabs the event object from Google Calendar
        event = calendarService.events().get(calendarId=TARGET_CALENDAR_ID, eventId=eventId).execute()

        splitList = event['description'].split('\n')

        splitList[2] = emailAddress

        finalDescription = '\n'.join(splitList)

        event['description'] = finalDescription

        updatedEventObject = calendarService.events().update(calendarId=TARGET_CALENDAR_ID, eventId=eventId, body=event).execute()

        print(f"Successfully updated event: {updatedEventObject.get('htmlLink')}")

    except Exception as e:
        print(f"[editEmail]: There was an issue changing the email address associated with this appointment {e}")

def editVehicle(eventId, vehicleInfo): 
    try: 
        calendarService = initializeCalendarService()

        event = calendarService.events().get(calendarId=TARGET_CALENDAR_ID, eventId=eventId).execute()

        splitList = event['description'].split('\n')

        splitList[3] = vehicleInfo

        finalDescription = '\n'.join(splitList)

        event['description'] = finalDescription 

        updatedEventObject = calendarService.events().update(calendarId=TARGET_CALENDAR_ID, eventId=eventId, body=event).execute() 

        print(f"Successfully updated event: {updatedEventObject.get('htmlLink')}")

    except Exception as e: 
        print(f"[editVehicle]: There was an issue changing the vehicle information associated with this appointment {e}")

def editServiceType(eventId, description): 
    try: 
        calendarService = initializeCalendarService() 
        event = calendarService.events().get(calendarId=TARGET_CALENDAR_ID, eventId=eventId).execute()

        splitList = event['description'].split('\n')

        splitList[4] = description

        finalDescription = '\n'.join(splitList)

        event['description'] = finalDescription

        updatedEventObject = calendarService.events().update(calendarId=TARGET_CALENDAR_ID, eventId=eventId, body=event).execute()
        
        print(f"Successfully updated service type {updatedEventObject.get('htmlLink')}")
    except Exception as e: 
        print(f"[editDescription]: There was an issue changing the service type and time {e}")

def editTimeSlot(eventId, startTime, duration): 
    try: 
        calendarService = initializeCalendarService()
        event = calendarService.events().get(calendarId=TARGET_CALENDAR_ID, eventId=eventId).execute()

        # starttime should be taking in a datetime object 
        # must give it timezone and iso format before processing the value 

        eventStart = startTime.astimezone(ZoneInfo('America/Los_Angeles'))
        eventEnd = (eventStart + timedelta(hours=duration)).astimezone(ZoneInfo('America/Los_Angeles'))

        event['start']['dateTime'] = eventStart.isoformat()
        event['end']['dateTime'] = eventEnd.isoformat()


        updatedEventObject = calendarService.events().update(calendarId=TARGET_CALENDAR_ID, eventId=eventId, body=event).execute()
        print(f"[editTimeslot]: Successfully changed the appointment time {updatedEventObject['htmlLink']}")

    except Exception as e: 
        print(f"[editTimeslot]: There as an issue changing the time for this appointment {e}")

#* Function is working as intended
def checkWeekendCondition(datetimeObject): 
    try:
        if datetimeObject.weekday() in [5, 6]: 
            # print("True")
            return True

        # print("False")
        return False 
    
    except Exception as e: 
        print(f"Enter a valid datetime object {e}")

#* Function to determine whether the requested day is valid [must be current or in the future]
def checkDayState(datetimeObject): 
    try: 
        currentDay = datetime.now()
        # print(f"[function]: This is currentDay {currentDay}")
        # print(f"[function]: This is datetimeObject {datetimeObject}")

        return datetimeObject >= currentDay

    except Exception as e: 
        print(f"This is not a valid datetime object {e}")

# This function will check to see if the requested day is within the business hours 
def checkWorkHour(datetimeObject): 
    tz = ZoneInfo('America/Los_Angeles')
    datetimeObject = datetimeObject.astimezone(tz)
    
    workHourBegin = datetimeObject.replace(hour=8, minute=0, second=0, microsecond=0)
    workHourEnd = datetimeObject.replace(hour=20, minute=0, second=0, microsecond=0)

    return workHourBegin <= datetimeObject < workHourEnd 


#* This returns a list of all the events going on for the day
def populateEventsForDay(datetimeObject): 
    #* we need to utilize the requested day to determine which day to check
    try: 
        calendarService = initializeCalendarService()
        # now = datetime.now()

        # since we are initially setting the appointment times in America/los_angeles
        formatTimeZone = ZoneInfo('America/Los_Angeles')
        # need to format the search query to look within this timezone information
        localizedTime = datetimeObject.replace(tzinfo=formatTimeZone)

        # print(f"[populateEventsforDay]: This is datetimeObject {datetimeObject}")

        # beginWorkHour = datetimeObject.replace(hour=8, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)
        # endWorkHour = datetimeObject.replace(hour=18, minute=0, second=0, microsecond=0, tzinfo=timezone.utc)

        # These variables are now working with the datetime object in america timezone
        beginWorkHour = localizedTime.replace(hour=8, minute=0, second=0, microsecond=0)
        endWorkHour = localizedTime.replace(hour=18, minute=0, second=0, microsecond=0)

        # print(f"[populateEventsforDay]: This is beginWorkHour {beginWorkHour}")
        # print(f"[populateEventsforDay]: This is endWorkHour {endWorkHour}")

        # Format the datetime objects in america timezone into iso format
        formatBegin = beginWorkHour.isoformat()
        formatEnd = endWorkHour.isoformat()

        # print(f"[populateEventsforDay]: This is formatBegin {formatBegin}")
        # print(f"[populateEventsforDay]: This is formatEnd {formatEnd}")
        
        # This now looks for all the america timezone events that we added initially 
        resultList = calendarService.events().list(
            calendarId=TARGET_CALENDAR_ID, 
            timeMin=formatBegin,
            timeMax=formatEnd, 
            singleEvents=True, 
            orderBy='startTime'
        ).execute()

        # print(f"[populateEventsForDay]: This is result list {resultList}")
        
        eventList = resultList.get('items', [])

        if not eventList: 
            # probably change the response to include which day is 'today'
            print(f"[populateEventsForDay]: No events found for today")

        # print(f"[populateEventForDay]: This is the eventList {eventList}")
        
        # populate the list 
        return eventList

    except Exception as e:
        print(f"[populateEventsForDay]: There was an error with gathering events for the day {e}") 

#* return an eventObject based on eventId 
def getEventObjectById(eventObjectId):
    """
    Returns an eventObject when you provide the eventId
    This is the eventObject from GOOGLE CALENDAR 
    it contains more metadata than the simplified one used in development
    """
    try: 
        calendarService = initializeCalendarService() 

        event = calendarService.events().get(calendarId=TARGET_CALENDAR_ID, eventId=eventObjectId).execute()

        return event 
    
    except Exception as e: 
        print(f"There was an error retrieving the event object {e}")
        return None 

def displayEventObjectInfo(eventObject): 
    descriptionList = eventObject['description'].split('\n')
    dtObjectStart = datetime.fromisoformat(eventObject['start']['dateTime'])
    dtObjectEnd = datetime.fromisoformat(eventObject['end']['dateTime'])

    var1 = (dtObjectEnd - dtObjectStart).total_seconds()           # find the difference in seconds
    diffHours = var1 / 3600                                        # convert the difference from seconds --> hours
    durationHour = int(diffHours)                                  # convert the object into integer


    eventObjectInfo=f"""
Name: {eventObject['summary']}
Vehicle: {descriptionList[3]}
Time: {convertDateTime(dtObjectStart, durationHour)}
    """
    return eventObjectInfo

#* this iteration uses the current day as a reference 
def populateAvailableSlots(): 
    try: 
        calendarService = initializeCalendarService()

        # Set the timezone to 'America/Los_Angeles'
        tz_los_angeles = ZoneInfo('America/Los_Angeles')

        # replacing the current datetime object with information of timezone and setting the time be 1AM [doesn't have to be 1am just some arbitary time that is before the working hours]
        currentDayObject = datetime.now(tz=tz_los_angeles).replace(hour=1, minute=0, second=0, microsecond=0)
        # currentDayObject = datetimeObject.astimezone(ZoneInfo('America/Los_Angeles')).replace(hour=1, minute=0, second=0, microsecond=0)

        startThreshhold = currentDayObject

        if startThreshhold.month == 12: 
            endOfMonth = startThreshhold.replace(year=startThreshhold.year + 1, month=1, day=1) - timedelta(seconds=1)
        else:
            endOfMonth = startThreshhold.replace(month=startThreshhold.month + 1, day=1) - timedelta(seconds=1)
        
        
        # declare our constraints of start day of the month and end day of the month 
        # in isoFormat()
        timeMin = startThreshhold.isoformat()
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
            print("[listAvailableTime]: There are no events this month")
        
        # (8, 20) signifies the hours from 8AM to 8PM  [24 hour format]
        # workHours = [(8, 20)] 
        availableSlots = {}

        # Iterating through every day of the current month 
        # starting from the first day of the current month
        currDay = startThreshhold
        weekendsFound = False 

        while currDay <= endOfMonth: 
            # if the current day is a weekend [5, 6] representing 
            # Saturday and Sunday respectively 
            if currDay.weekday() in [5, 6]: 
                weekendsFound = True 

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
                timeStart = currDay.replace(hour=8, minute=0, second=0, microsecond=0)
                timeEnd = currDay.replace(hour=20, minute=0, second=0, microsecond=0)

                # This is essentially representing the company's working hours
                timeAvailable = [(timeStart, timeEnd)]

                # iterating over all the events that happen to land on a weekend
                for event in weekendObjectList: 
                    """ From the event object that we are processing, 
                    process that specific event object's start and end time(s)
                    """
                    eventStart = datetime.fromisoformat(event['start'].get('dateTime'))
                    eventEnd = datetime.fromisoformat(event['end'].get('dateTime'))

                    # split available times around the event
                    newAvailableTimes = []
                    for workStart, workEnd in timeAvailable: 
                        # If event starts before the workEnd and ends after the workStart, it overlaps
                        if eventStart <= workEnd and eventEnd >= workStart: 
                            # If the event starts after the workStart, keep the time before the event
                            if workStart < eventStart: 
                                #* the timedelta here should be replaced with the type of cleaning [interior/exterior = 1hr, both = 2hr]
                                newAvailableTimes.append((workStart, (eventStart - timedelta(hours=1) )))
                                # newAvailableTimes.append((workStart, eventStart))
                            
                            # If the event ends before the workEnd, keep the time after the event
                            if eventEnd < workEnd: 
                                newAvailableTimes.append((eventEnd, workEnd))
                        else: 
                            # No overlap, so keep the original time slot
                            newAvailableTimes.append((workStart, workEnd))
                            
                    timeAvailable = newAvailableTimes
                    
                availableSlots[currDay.strftime('%Y-%m-%d')] = timeAvailable
            
            # move to the next day
            currDay += timedelta(days=1)
            
        # if no weekends were found, then we need to increment the next and search
        if not weekendsFound: 
            nextMonth = startThreshhold.replace(day=1)
            if nextMonth.month == 12: 
                nextMonth = nextMonth.replace(year=nextMonth.year + 1, month=1)
            else: 
                nextMonth = nextMonth.replace(month=nextMonth.month + 1)

            nextMonthEnd = nextMonth.replace(day=1).replace(month=nextMonth.month + 1) - timedelta(seconds=1) 

            # used in the query for the Google Calendar 
            timeMinNextMonth = nextMonth.isoformat()
            timeMaxNextMonth = nextMonthEnd.isoformat()

            # Query events for the next month
            resultListNextMonth = calendarService.events().list(
                calendarId=TARGET_CALENDAR_ID,
                timeMin=timeMinNextMonth,
                timeMax=timeMaxNextMonth,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

            eventListNextMonth = resultListNextMonth.get('items', [])

            nextCurrDay = nextMonth 

            while nextCurrDay <= nextMonthEnd: 
                if nextCurrDay.weekday() in [5, 6]: 
                    weekendsFound = True

                    weekendObjectList = [ 
                        event for event in eventListNextMonth
                        if event['start'].get('dateTime', event['start'].get('date')).startswith(nextCurrDay.strftime('%Y-%m-%d'))
                    ]

                    timeStart = nextCurrDay.replace(hour=8, minute=0, second=0, microsecond=0)
                    timeEnd = nextCurrDay.replace(hour=20, minute=0, second=0, microsecond=0)

                    timeAvailable = [(timeStart, timeEnd)]

                    for event in weekendObjectList: 
                        eventStart = datetime.fromisoformat(event['start'].get('dateTime'))
                        eventEnd = datetime.fromisoformat(event['end'].get('dateTime'))

                        newAvailableTimes = [] 
                        for workStart, workEnd in timeAvailable: 
                            if eventStart <= workEnd and eventEnd >= workStart: 
                                if workStart < eventStart: 
                                    newAvailableTimes.append((workStart, (eventStart - timedelta(hours=1) )))
                                
                                if eventEnd < workEnd: 
                                    newAvailableTimes.append((eventEnd, workEnd))
                            
                            else: 
                                newAvailableTimes.append((workStart, workEnd))

                        timeAvailable = newAvailableTimes

                    availableSlots[nextCurrDay.strftime('%Y-%m-%d')] = timeAvailable
            
                nextCurrDay += timedelta(days=1)

        return availableSlots
    
    except Exception as e: 
        print(f"[listAvailableTimeValidMonth]: There was an error displaying the available weekend times {e}") 

# This function is used for the create storyline when we are initially checking only if the client requested time is available from the slots on that requested day
def isTimeAvailable(startTimeObject, duration): 
    """ 
    Takes in a datetimeObject and the duration of the specific service type 
    """
    eventStart = startTimeObject.astimezone(ZoneInfo('America/Los_Angeles'))
    eventEnd = eventStart + timedelta(hours=duration)

    eventDate = startTimeObject.strftime('%Y-%m-%d')

    # availableSlots = populateAvailableSlots(startTimeObject)
    availableSlots = populateAvailableSlots()

    print(f"This is available slots {availableSlots}")

    # check if the date has available slots 
    if eventDate not in availableSlots: 
        print(f"No availability on {eventDate}")
        return False 

    # iterate through avail slots for that date 
    for startTime, endTime in availableSlots[eventDate]: 
        if eventStart >= startTime and eventEnd <= endTime: 
            return True 
    
    # otherwise return false 
    return False 

# this one is going to check for a possible extension ONLY and nothing else 
def checkTimeExtension(datetimeObject): 
    """
    The function will take in a startTime datetime object and the duration of the appointment from the initial startTime  
    ** Note: does not seem to detect manual events added directly on the calendar, but it will detect events made through the bot
    """

    eventStart = datetimeObject.astimezone(ZoneInfo('America/Los_Angeles')) # 8am
    eventEnd = eventStart + timedelta(hours=1)                              # 9am

    extensionEnd = eventEnd + timedelta(hours=1)                            #10am

    # used to determine which key to look into in timeList
    eventDate = eventStart.strftime('%Y-%m-%d')

    availableTimeList = populateAvailableSlots() 
    print(f"This is timeList {availableTimeList}")

    # if the key is not in the list [we have no availability on that date]
    if eventDate not in availableTimeList:
        return False 

    for start, end in availableTimeList[eventDate]:
        # Check if the extension period (9 AM - 10 AM) is within an available slot.
        if eventEnd >= start and extensionEnd <= end:
            return True

    return False