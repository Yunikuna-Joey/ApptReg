# Flask imports
from flask import Flask, request, jsonify

# helper file imports
from webhookhelper import extractSenderIdFromPayload, initializeNgrokService, getUserAgentHeader, extractMessageContentFromPayload
from scenario import additionScenario

# database imports
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sessionManager import initializeDatabase

import requests

from dotenv import load_dotenv
import os 
load_dotenv()

app = Flask(__name__)
#* initialize a current session and database connected to the session-changes
engine = create_engine('sqlite:///sessions.db', echo=True)
Session = sessionmaker(bind=engine)
dbSession = Session()
initializeDatabase(engine)

verifyToken = os.getenv('VERIFY_TOKEN')
accessList = [os.getenv('USER_AGENT_FIELD'), os.getenv('WEBHOOK'), os.getenv('IG_MSG_AGENT')]

# the route is the url 
# function is nothing special
@app.route('/')
def homePage():
    try: 
        if getUserAgentHeader() != os.getenv('USER_AGENT_FIELD'): 
            return 'You do not have access to this'

        else: 
            return 'Hello World'
        
    except Exception as e: 
        return f'There was an error processing this request: {e}'
    
@app.route('/webhook', methods=['GET'])
def verifyWebhook():
    """ 
    Meta API will send a request to the webhook | server to see if the webhook/server returns 
    the correct string/token [handshake] that allows for valid use of api function(s) 
    """ 

    try: 
        if getUserAgentHeader() not in accessList: 
            return 'Verification failed', 403
    
        else:
            if request.method == 'GET':
                # parse the verification parameters from Meta request
                mode = request.args.get('hub.mode')
                token = request.args.get('hub.verify_token')
                challenge = request.args.get('hub.challenge')

                print(f"This is the mode {mode} \n")
                print(f"This is the token {token} \n")
                print(f"This is the challenge {challenge}\n")


                # determine if the mode is subscribe and if the handshake was correct
                if mode == 'subscribe' and token == verifyToken: 
                    # return the handshake back to meta with a success code
                    return challenge, 200 
    
    except Exception as e:
        return f"[Except_Block_VerifyWebhook]: There was an error processing the request {e}" 
    
@app.route('/webhook', methods=['POST'])
def processPostRequest():
    try: 
        # implement a barrier for detecting valid request
        if getUserAgentHeader() not in accessList:
            return 'Verification failed', 401

        """ 
        The webhook will listen for a Message Event from Meta API 
        We extract the message content from the webhook request 
        We extract the message sender ID for session management

        Pass it into our logic for attempting an appointment
            => Option1: What if we grab the intent from the first message? 
                So if message has intent: proceed with logic 
                (issue: this is a while loop, so how do we keep chat persistence(?) 
                as we are receiving Message Events one at a time (one message at a time))
                
                If no intent: we just generate a response from the LLM 
                
        """
        # payload will have the information that we need to extract coming from meta api 
        payload = request.get_json()

        # this will help determine how to handle the payload request coming into the endpoint
        payloadIdentifier = payload['entry'][0]['messaging'][0]             # so far we keep track of a message event and a message_read(app reading the message from the client)

        # This will handle a normal message event 
        if 'message' in payloadIdentifier and payloadIdentifier['sender']['id'] != os.getenv('INSTAGRAM_PAGE_ID'):          # we need a condition so that the bot doesn't attempt to process itself
            messageContent = extractMessageContentFromPayload(payload).strip()
            senderId = extractSenderIdFromPayload(payload)

            # implement the chatbot logic 
            responseMessageContent = additionScenario(senderId, messageContent, dbSession)
            
            # debugging variables
            status, requestResponse = sendMsg(senderId, responseMessageContent)

            # print(f"Send message status: {status}, response: {requestResponse}")
        
        # This will handle a read message event
        elif 'read' in payloadIdentifier:
            print("[Event_Detection]: Triggered a read_message event")
            return jsonify({"status": "ok"}), 200
        
        # This will handle a message send event
        elif 'is_echo' in payloadIdentifier['message']: 
            print("[Event_Detection]: Triggered a message send event")
            return jsonify({"status": "ok"}), 200

        # this should catch any other unhandled event that can be used for debugging
        else: 
            print("[Webhook_Endpoint]: This is an unhandled event type")
            return jsonify({"status": "Unhandled event type"}), 400

        # After processing the request, we need to return a 200 success code 
        return jsonify({"status": "ok"}), 200

    except Exception as e:
        print(f"[Except_Block_ProcessRequest]: There was an error with processing the request {e}")
        return f"[Except_Block_ProcessRequest]: There was an error processing the request {e}", 403

# Allows for meta app to send a message to the requested user 
def sendMsg(userId, messageContent): 
    # url = f"https://graph.instagram.com/v21.0/{os.getenv('INSTAGRAM_PAGE_ID')}/messages"
    # simplified, but should look into what the full url should be... 
    url = f"https://graph.instagram.com/v21.0/me/messages"

    payload = { 
        'recipient': {'id': userId}, 
        'message': {'text': messageContent}, 
        'messaging_type': 'RESPONSE'
    }

    headers = { 
        'Content-Type': 'application/json', 
        'Authorization': f"Bearer {os.getenv('INSTAGRAM_UAT')}"
    }

    response = requests.post(url, json=payload, headers=headers)
    
    # print(f"Response Status: {response.status_code}, Response Text: {response.text}")
    return response.status_code, response.text

if __name__ == '__main__': 
    initializeNgrokService()

    app.run(port=5500)