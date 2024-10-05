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
        addr=5000, 
        domain=f"{os.getenv('NGROK_DOMAIN')}",
        verify_webhook="FACEBOOK_GRAPH_API", 
        verify_webhook_secret=os.getenv('APP_SECRET')
    )

    print(f"ngrok tunnel is running at: {ngrokTunnel.url}")

def getUserAgentHeader(): 
    userAgentField = request.headers.get('User-Agent')
    # print(f"This is the userAgentField {userAgentField}")
    return userAgentField

