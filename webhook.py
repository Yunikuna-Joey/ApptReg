from flask import Flask, request, jsonify, abort
from webhookhelper import initializeNgrokService, getUserAgentHeader
import ngrok
import hashlib
import hmac

from dotenv import load_dotenv
import os 
load_dotenv()

app = Flask(__name__)

verifyToken = os.getenv('VERIFY_TOKEN')

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
        if getUserAgentHeader() != os.getenv('USER_AGENT_FIELD'): 
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
        # signature = request.headers.get('X-Hub-Signature-256')

        # if not signature: 
        #     abort(403, "Missing Signature")

        # signature = signature.split('sha256=')[-1].strip()

        payload = request.get_data()
        print(f"[First Call]: This is the incoming payload: {payload}")

        # expectedSignature = hmac.new(
        #     os.getenv('APP_SECRET').encode('utf-8'),
        #     payload, 
        #     hashlib.sha256
        # ).hexdigest()

        # if not hmac.compare_digest(expectedSignature, signature): 
        #     abort(403, "Invalid signature.")

        print("We are in the post method conditional")
        # payload will have the information that we need to extract coming from meta api 
        payload = request.get_json()
        
        print(f"[Second Call]: This is the incoming payload: {payload}")

    except Exception as e:
        return f"There was an error processing the request {e}" 

    
if __name__ == '__main__': 
    initializeNgrokService()

    app.run(port=5000)