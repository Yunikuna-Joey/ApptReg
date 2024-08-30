# Loads service account credentials
from google.oauth2.service_account import Credentials
# Creates the connection to one of Google's product API (in our case, Google Calendar)
from googleapiclient.discovery import build 

#* Emailing purposes
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv
import os 
import google.generativeai as genai

load_dotenv()

#* Global registration variables 
apiKey = os.getenv('API_TOKEN')
genai.configure(api_key=apiKey)
model = genai.GenerativeModel(os.getenv('API_MODEL'))

#* Email configuration
smtp_server = os.getenv('EMAIL_SERVER')
smtp_port = os.getenv('EMAIL_PORT')
smtp_username = os.getenv('EMAIL_CRED')
smtp_password = os.getenv('PASSWORD_CRED')

# setup MIME 
message = MIMEMultipart()
message['From'] = smtp_username
message['To'] = smtp_password 
message['Subject'] = "Appointment Confirmation"

body = """ 
Hello insert_customer_name_here, 

This message is a confirmation of your car detailing appointment. 

Details: 
- **Car**: Year, make, model 
- **Location**: Address 
- **Type of Cleaning**: Interior, exterior, both
- **Start Time**: Format the time as Month Name, Day, Year @ 12 hour format time 
- **End Time**: Format the time as Month Name, Day, Year @ 12 hour format time 

Feel free to add this event in your Google Calendar automatically by clicking the .ics file.

Best regards,
Ten (Just an AutoBot)

Do not reply back to this message, inbox is unmonitored.

"""

message.attach(MIMEText(body, 'plain'))

# email server connection
# server = smtplib.SMTP(smtp_server, smtp_port)
# server.starttls()
# server.login(smtp_username, smtp_password)
# server.sendmail(smtp_username, os.getenv("TEST_USER"), message.as_string())
# server.quit()


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

    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(smtp_username, smtp_password)
    server.sendmail(smtp_username, os.getenv("TEST_USER"), message.as_string())
    server.quit()
