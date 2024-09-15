import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from helper import convertDateTime
from datetime import timedelta

from dotenv import load_dotenv
load_dotenv()
import os

#* Email configuration
smtp_server = os.getenv('EMAIL_SERVER')
smtp_port = os.getenv('EMAIL_PORT')
smtp_username = os.getenv('EMAIL_CRED')
smtp_password = os.getenv('PASSWORD_CRED')

# Format the confirmation message object [need to add in the .ics file attached to the message]
def createConfirmationMessageExample(): 
    #* setup MIME 
    message = MIMEMultipart()
    # setup to, from, and subject line portion of the email
    message['From'] = smtp_username
    message['To'] = os.getenv('TEST_USER') # swap this to recipient user email
    message['Subject'] = "Appointment Confirmation"

    #* Message content
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

    # convert message to plain text
    message.attach(MIMEText(body, 'plain'))

    print("[createMessageHeader]: Message object created successfully.")

#     return message
def createConfirmationMessage(customerName, vehicleInfo, address, cleanType, startTime): 
    #* setup MIME 
    message = MIMEMultipart()
    # setup to, from, and subject line portion of the email
    message['From'] = smtp_username
    message['To'] = os.getenv('TEST_USER') # swap this to recipient user email
    message['Subject'] = "Appointment Confirmation"

    #* Message content
    body = f""" 
    Hello {customerName}, 

    This message is a confirmation of your car detailing appointment. 

    Details: 
    - Car: {vehicleInfo}
    - **Location**: {address} 
    - **Type of Cleaning**: {cleanType}
    - **Time**: {convertDateTime(startTime)} 

    Feel free to add this event in your Google Calendar automatically by clicking the .ics file.

    Best regards,
    Ten (Just an AutoBot)

    Do not reply back to this message, inbox is unmonitored.

    """

    # convert message to plain text
    message.attach(MIMEText(body, 'plain'))

    print("[createMessageHeader]: Message object created successfully.")

    return message

def createDeleteConfirmationMessage(recipientEmail): 
    # setup MIME 
    message = MIMEMultipart()
    # setup message headers 
    message['From'] = smtp_username
    message['To'] = recipientEmail
    message['Subject'] = 'Appointment Cancellation'
    
    #* Message content 
    body = """ 
    Hello insert_customer_name_here, 

    This message is to inform you of your appointment cancellation. 

    Cancelled appointment details: 
    **Car**: Year, Make, Model 
    **Location**: Address 
    **Type of Cleaning**: Interior, exterior, both
    **Start Time**: Format the time as Month Name, Day, Year @ 12 hour format time 
    **End Time**: Format the time as Month Name, Day, Year @ 12 hour format time 

    Feel free to re-book your appointment to a time that works best for you. 
    Have a great day, 
    Ten (Just an AutoBot)

    Do not reply back to this message, inbox is unmonitored.
    """

    message.attach(MIMEText(body, 'plain'))

    print("[createDeleteConfirmationMessage]: Message object created successfully.")
    print(f"This is the message delete confirmation {message}")
    return message 

def createEditConfirmationMessage(recipientEmail): 
    # setup MIME 
    message = MIMEMultipart()
    # setup message headers 
    message['From'] = smtp_username
    message['To'] = recipientEmail
    message['Subject'] = 'Appointment Modification'
    
    #* Message content 
    body = """ 
    Hello insert_customer_name_here, 

    This message is to inform you of your appointment change. 

    New appointment details: 
    **Car**: Year, Make, Model 
    **Location**: Address 
    **Type of Cleaning**: Interior, exterior, both
    **Start Time**: Format the time as Month Name, Day, Year @ 12 hour format time 
    **End Time**: Format the time as Month Name, Day, Year @ 12 hour format time 

    Thank you for booking with us and we hope to see you soon! 

    Have a great day, 
    Ten (Just an AutoBot)

    Do not reply back to this message, inbox is unmonitored.
    """

    message.attach(MIMEText(body, 'plain'))

    print("[createEditConfirmationMessage]: Message object created successfully.")
    print(f"This is the message edit confirmation {message}")
    return message 

# Send the message object to the recipient email address
def sendEmail(messageObject, recipientEmailAddress): 
    # create the server with port # 
    server = smtplib.SMTP(smtp_server, smtp_port)
    # create the protocol
    server.starttls()
    # log into the server with the company username and password
    server.login(smtp_username, smtp_password)

    # This is a test line 
    # server.sendmail(smtp_username, os.getenv("TEST_USER"), messageObject.as_string())

    # This will send the email... .sendmail(fromUser, toUser, convertMessageToString())
    server.sendmail(smtp_username, recipientEmailAddress, messageObject.as_string())

    print("[sendEmail]: Email was sent successfully.")

    # exit the server, it does not need to stay on, only when it needs to send emails
    server.quit()

