#* Emailing purposes
from emailService import * 
from eventService import * 
import datetime 

from dotenv import load_dotenv
import os 
load_dotenv()

import google.generativeai as genai

#* Global registration variables 
apiKey = os.getenv('API_TOKEN')
genai.configure(api_key=apiKey)
model = genai.GenerativeModel(os.getenv('API_MODEL'))



#* Example request [refer back as necessary]
def exampleClientRequest():
    response = model.generate_content("What is the most popular food?")
    print(response.text)

def example(): 
    response = model.generate_content("Hello, I would like to schedule an appointment")
    print(response.text)

def main(): 
    #* Test scenario 
        # create an eventObject 
        # add event into Calendar
        # send email about appointment confirmation
    # eventObject = createEventObject()
    # addEvent(eventObject)
    # messageObject = createConfirmationMessage()
    # sendEmail(messageObject, os.getenv('TEST_USER'))
    # displayAllEvents()
    print("Hello world")
    newStartTime = datetime.datetime(2024, 9, 1, 14, 0) # September 1 2024, 2:00 PM
    newEndTime = datetime.datetime(2024, 9, 1, 15, 0)   # September 1 2024, 3:00 PM
    editEvent("flq1ho9lfpan7ugr1mgjtedadk", newStartTime, newEndTime)


if __name__ == "__main__": 
    main()
