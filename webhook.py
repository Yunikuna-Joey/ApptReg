from flask import Flask, request, jsonify
from webhookhelper import extractSenderIdFromPayload, initializeNgrokService, getUserAgentHeader, extractMessageContentFromPayload
from scenario import additionScenario

import requests

from dotenv import load_dotenv
import os 
load_dotenv()

app = Flask(__name__)

verifyToken = os.getenv('VERIFY_TOKEN')
accessList = [os.getenv('USER_AGENT_FIELD'), os.getenv('WEBHOOK')]

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
        return f"There was an error processing the request {e}" 
    
@app.route('/webhook', methods=['POST'])
def processPostRequest():
    try: 
        # implement a barrier for detecting valid request
        if getUserAgentHeader() not in accessList:
            return 'Verification failed', 401

        else:
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

            messageContent = extractMessageContentFromPayload(payload)
            senderId = extractSenderIdFromPayload(payload)

            # implement the chatbot logic 
            responseMessageContent = additionScenario(senderId, messageContent)
            
            status, requestResponse = sendMsg(responseMessageContent, senderId)

            print(f"Send message status: {status}, response: {requestResponse}")
            
            # print(f"[Second Call]: This is the incoming payload: {payload}")

            # After processing the request, we need to return a 200 success code 
            # return 'Message received', 200 
            return jsonify({"status": "ok"}), 200

    except Exception as e:
        print(f"There was an error with processing the request {e}")
        return f"There was an error processing the request {e}", 403

def sendMsg(userId, messageContent): 
    # url = f"https://graph.facebook.com/v21.0/{os.getenv('INSTAGRAM_PAGE_ID')}/messages"
    url = f"https://graph.instagram.com/v21.0/{os.getenv('INSTAGRAM_PAGE_ID')}/messages"


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

    print(f"Response Status: {response.status_code}, Response Text: {response.text}")
    return response.status_code, response.text

if __name__ == '__main__': 
    initializeNgrokService()

    app.run(port=5000)