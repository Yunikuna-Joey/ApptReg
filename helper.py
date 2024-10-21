"""
    This file's purpose is to host some helper function(s) for various mini-tasks
"""
from datetime import timedelta, datetime
import platform 
import re 
import dns.resolver
import requests

# converts datetime objects for the listAvailable function 
def convertDateTime(dateTimeObject, duration): 
    # this looks like 'September 15, 2024 at 6:00AM'
    # formattedTime = dateTimeObject.strftime("%B %d, %Y at %-I:%M %p")

    # endTime = dateTimeObject + timedelta(hours=1)
    # formattedEndTime = endTime.strftime("%-I:%M %p")

    # Windows strftime manipulation
    if platform.system() == 'Windows':
        # Use the format without `%-` for Windows (leading zeros remain)
        formattedTime = dateTimeObject.strftime("%B %d, %Y at %I:%M %p")
        endTime = dateTimeObject + timedelta(hours=duration)
        formattedEndTime = endTime.strftime("%I:%M %p")
        
    # MacOS strftime manipulation
    else:
        # Use `%-I` for Unix-based systems (no leading zero in hour)
        formattedTime = dateTimeObject.strftime("%B %d, %Y at %-I:%M %p")
        endTime = dateTimeObject + timedelta(hours=duration)
        formattedEndTime = endTime.strftime("%-I:%M %p")

    return f"{formattedTime} - {formattedEndTime}" 

def resetObjectValues(dataObject): 
    if isinstance(dataObject, dict): 
        for key in dataObject: 
            dataObject[key] = None 
    
    elif isinstance(dataObject, str): 
        dataObject = ""

def emailChecker(email): 
    # expression to determine userInput follows a valid email format
    emailRegex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'

    # return false if the formats do not match
    if not re.match(emailRegex, email): 
        return False 

    # extract the domain portion of the email [everything after the @ sign]
    domain = email.split('@')[-1]

    # print(f"This is the value of domain {domain}")

    # check if the domain has a Mail exchange record
    try: 
        dns.resolver.resolve(domain, 'MX')
        return True 
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN) : 
        return False

def phoneNumberChecker(phoneNumber): 
    """ 
        Valid: 
            (111) 111-1111
            111-111-1111
            111.111.1111
            111 111 1111 
            1111111111
    """
    hyphenRegex = r'^(\+?1\s?)?(\([0-9]{3}\)|[0-9]{3})[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}$'
    return True if re.match(hyphenRegex, phoneNumber) else False 
    
def carDescriptionchecker(carDescription): 
    # give an upper bound of +1 to the current year [possibility]
    currYear = datetime.now().year + 1 
    # print(currYear)

    #* year/make/model [4 digit year, Car brand, car model]
    descriptionRegex = r'^(19\d{2}|20[01]\d|20[2-4]\d)\s+([A-Za-z]+(?:[ -][A-Za-z]+)*)\s+([A-Za-z0-9]+(?:[ -][A-Za-z0-9]+)*)$'

    match = re.match(descriptionRegex, carDescription)

    if not match: 
        return False 
    
    year = int(match.group(1))
    # print(f"The value of year {year}")

    return True if 1980 <= year <= currYear else False 

def serviceTypeChecker(serviceType): 
    """
    Checks if the user input is a valid service type 
    """
    validInput = ['interior', 'Interior', 'exterior', 'Exterior', 'both', 'Both']

    if serviceType not in validInput: 
        return False 
    
    return True 

def displayConfirmationMessage(eventObject, duration): 
    confirmationMsg = f"""
Please confirm your details - 
Name: {eventObject['name']}
Phone: {eventObject['number']}
Email: {eventObject['email']}
Car: {eventObject['carModel']}
Location: {eventObject['location']}
Cleaning: {eventObject['description']}
Date: {eventObject['start'].strftime('%B %d, %Y')}
Time: {eventObject['start'].strftime('%I:%M %p')} - {(eventObject['start'] + timedelta(hours=duration)).strftime('%I:%M %p')}
    """
    # print(confirmationMsg)
    return confirmationMsg

def serviceToHours(serviceType): 
    """ 
    This will take in a string (service) then retrieve the hours associated with that specific service (string)
    """
    serviceMap = { 
        'interior': 1, 
        'exterior': 1,
    }

    if serviceType == 'interior': 
        return serviceMap.get(serviceType, 0) 
    
    elif serviceType == 'exterior': 
        return serviceMap.get(serviceType, 0) 

    else: 
        return 2
    
def generatePrompt(field): 
    """ 
        This will allow for customization of different questions that can be asked 
        to fill in for the missing (necessary) information to pack the 
        event object 
    """

    prompts = {
        'name': "What is your name?",
        'number': "What is your phone number?",
        'email': "What is your email address?",
        'carModel': "What is the year/make/model of your vehicle?", 
        'location': "Please provide your address if you would like for us to come to you, otherwise enter 'your facility'. ",
        'description': "What kind of wash are you looking for? We have interior, exterior, or you can say both",
        'start': "What day and time are you lookin for? Please specify the date and time in this format 'September 18 at 12PM'",
    }

    return prompts.get(field, "Could you provide more information?")

def getInstagramUsername(userId, metaAccessToken): 
    """
    This converts a userId into an official Instagram username
    """
    url = f"https://graph.instagram.com/{userId}"
    params = { 
        'fields': 'username', 
        'access_token': metaAccessToken
    }

    response = requests.get(url, params=params)

    if response.status_code == 200: 
        data = response.json() 
        return data['username']

    else: 
        print(f"Error: {response.status_code}")
        return None 