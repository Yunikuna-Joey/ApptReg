from flask import request
from dotenv import load_dotenv

import ngrok 
import os 

load_dotenv()


def initializeNgrokService(): 
    """
    This helper function handles setting up the ngrok tunnel that allows the local server to be seen by the meta api
    """
    # previous iterations of intializing tunnel [refer as necessary]
    # link the local server from Flask (port #) to the domain, with the basic auth credentials set up
    # publicUrl = ngrok.connect(
    #     addr=5000, 
    #     domain=f"{os.getenv('NGROK_DOMAIN')}",
    #     basic_auth=[f"{username}:{pw}"]
    # )

    # publicUrl = ngrok.connect(
    #     addr=5000, 
    #     domain=f"{os.getenv('NGROK_DOMAIN')}"
    # )

    # need to set auth token of who instantiated the tunnel
    ngrok.set_auth_token(os.getenv('NGROK_TOKEN'))

    # start the tunnel with these parameters
    ngrokTunnel = ngrok.connect(
        proto="http", 
        addr=5500, 
        domain=f"{os.getenv('NGROK_DOMAIN')}"
    )

    print(f"ngrok tunnel is running at: {ngrokTunnel.url}")

def getUserAgentHeader(): 
    """
    Returns the User-Agent field portion of a request package
    """
    userAgentField = request.headers.get('User-Agent')
    # print(f"This is the userAgentField {userAgentField}")
    return userAgentField

def extractMessageContentFromPayload(payload): 
    """ 
    Return the message content from the payload sent from Meta API 
    The payload should already in JSON format.
    """

    messageContent = payload['entry'][0]['messaging'][0]['message']['text']

    return messageContent

def extractSenderIdFromPayload(payload): 
    """
    Return the senderId from the message payload sent from Meta API
    The payload should already be in JSOn format.
    """
    
    senderId =  payload['entry'][0]['messaging'][0]['sender']['id']

    return senderId