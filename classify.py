import json
from eventService import * 

def classifyUserAction(model, userInput):
    prompt = f"""
    You are an AI assistant. Your task is to classify the user's intent and extract relevant details.
    The user will provide instructions related to calendar events, such as creating, modifying, or deleting an event.

    For example:
    - If the user says "I want to schedule a car wash on Sept 2 at 10 AM at 123 Main St", classify the intent as "create".
    - If the user says "Change my appointment to 11 AM", classify the intent as "modify".
    - If the user says "Cancel my appointment", classify the intent as "delete".

    Provide the output in the following JSON format:
    {{
        "intent": "create/modify/delete",
        "title": "car year make model",
        "location": "event location (if applicable)",
        "start_time": "start time (if applicable)",
        "end_time": "end time (if applicable)",
        "event_id": "event ID (if applicable)"
    }}

    User input: "{userInput}"
    """

    # Generate the response from the LLM
    response = model.generate_content(prompt)
    print("[LLM Response]:", response.text)

    # Parse the response as JSON
    try:
        result = json.loads(response.text)
        return result
    except json.JSONDecodeError:
        print("[Error]: Failed to decode LLM response")
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
        