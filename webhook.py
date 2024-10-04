from flask import Flask, request, jsonify 
import ngrok

from dotenv import load_dotenv
import os 
load_dotenv()

app = Flask(__name__)

verifyToken = os.getenv('VERIFY_TOKEN')

@app.route('/')
def hello():
    return "Hello, World! This is served via Ngrok with basic auth."

@app.route('/webhook', methods=['GET'])
def verifyWebhook():
    """ 
    Meta API will send a request to the webhook | server to see if the webhook/server returns 
    the correct string/token [handshake] that allows for valid use of api function(s) 
    """ 

    # parse the verification parameters from Meta request
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')

    # determine if the mode is subscribe and if the handshake was correct
    if mode == 'subscribe' and token == verifyToken: 
        # return the handshake back to meta with a success code
        return challenge, 200 
    
    # handshake was not correct, return with a forbidden code 
    else: 
        return 'Verification failed', 403
    
if __name__ == '__main__': 
    # set up ngrok tunnel 
    ngrok.set_auth_token(os.getenv('NGROK_TOKEN'))

    username = os.getenv('BAUTH_USER')
    pw = os.getenv('BAUTH_PW')

    listener = ngrok.forward("localhost:5000",
                            authtoken=os.getenv('NGROK_TOKEN'),
                            basic_auth=[f"{username}:{pw}"])

    print(f"Ingress established at: {listener.url()}")

    app.run(port=5000)