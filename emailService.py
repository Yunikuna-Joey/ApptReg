import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv
import os

#* Email configuration
smtp_server = os.getenv('EMAIL_SERVER')
smtp_port = os.getenv('EMAIL_PORT')
smtp_username = os.getenv('EMAIL_CRED')
smtp_password = os.getenv('PASSWORD_CRED')

# Format the message object 
def createMessageHeader(): 
    #* setup MIME 
    message = MIMEMultipart()
    # setup to, from, and subject line portion of the email
    message['From'] = smtp_username
    message['To'] = os.getenv('TEST_USER') 
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
    messageObject = message.attach(MIMEText(body, 'plain'))

    print("[createMessageHeader]: Message object created successfully.")

    return messageObject

# Send the message object to the recipient email address
# def sendEmail(messageObject, recipientEmailAddress): 
#     # create the server with port # 
#     server = smtplib.SMTP(smtp_server, smtp_port)
#     # create the protocol
#     server.starttls()
#     # log into the server with the company username and password
#     server.login(smtp_username, smtp_password)

#     # This is a test line 
#     # server.sendmail(smtp_username, os.getenv("TEST_USER"), messageObject.as_string())

#     # This will send the email... .sendmail(fromUser, toUser, convertMessageToString())
#     server.sendmail(smtp_username, recipientEmailAddress, messageObject.as_string())

#     print("[sendEmail]: Email was sent successfully.")

#     # exit the server, it does not need to stay on, only when it needs to send emails
#     server.quit()

def sendEmail(message_object, recipient_email_address):
    try:
        # Create the server connection
        server = smtplib.SMTP(smtp_server, smtp_port)
        
        # Start the TLS protocol
        server.starttls()
        
        # Log into the server with the company username and password
        server.login(smtp_username, smtp_password)
        
        # Send the email
        server.sendmail(smtp_username, recipient_email_address, message_object.as_string())
        print("[send_email]: Email was sent successfully.")
    
    except smtplib.SMTPException as e:
        print(f"[send_email]: Failed to send email. Error: {e}")
    
    finally:
        # Exit the server
        server.quit()