import json
import os 
from eventService import * 
from dotenv import load_dotenv

load_dotenv()

# def classifyUserAction(model, userInput):
#     # Generate the response from the LLM
#     response = model.generate_content(userInput)
#     print("[LLM Response]:", response.text)

#     # Parse the response as JSON
#     try:
#         result = json.loads(response.text)
#         return result
#     except json.JSONDecodeError:
#         print("[Error]: Failed to decode LLM response")
#         return None

#* New attempt at function
def classifyUserAction(model, userInput):  # returns a string
    response = model.generate_content(userInput)
    print(f"[HelperBot]: {response.text}")

    try: 
        result = response.text
        return result
    except Exception as e: 
        print(f"[Error]: An error occurred-- {e}")
        return None 

    
def processUserAction(output): 
    intent = output.get('intent')

    if intent == 'create': 
        eventObject = createEventObject(
            output.get('title'),
            output.get('location'), 
            output.get('description'),
            output.get('start')
        )
        addEvent(eventObject)
        print('[processUserAction]: Event added successfully.')
        return('[processUserAction]: Function ran i guess')

    # the other intent's require an eventId and not an eventObject
    else: 
        return ("I didn't understand that, Please specify what you are looking to do.")
        