"""
    This file's purpose is to host some helper function(s) for various mini-tasks
"""
from datetime import timedelta, datetime
import platform 
import re 
import dns.resolver

# converts datetime objects for the listAvailable function 
def convertDateTime(dateTimeObject): 
    # this looks like 'September 15, 2024 at 6:00AM'
    # formattedTime = dateTimeObject.strftime("%B %d, %Y at %-I:%M %p")

    # endTime = dateTimeObject + timedelta(hours=1)
    # formattedEndTime = endTime.strftime("%-I:%M %p")

    # Windows strftime manipulation
    if platform.system() == 'Windows':
        # Use the format without `%-` for Windows (leading zeros remain)
        formattedTime = dateTimeObject.strftime("%B %d, %Y at %I:%M %p")
        endTime = dateTimeObject + timedelta(hours=1)
        formattedEndTime = endTime.strftime("%I:%M %p")
        
    # MacOS strftime manipulation
    else:
        # Use `%-I` for Unix-based systems (no leading zero in hour)
        formattedTime = dateTimeObject.strftime("%B %d, %Y at %-I:%M %p")
        endTime = dateTimeObject + timedelta(hours=1)
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

    print(f"This is the value of domain {domain}")

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
    print(currYear)

    #* year/make/model [4 digit year, Car brand, car model]
    descriptionRegex = r'^(19\d{2}|20[01]\d|20[2-4]\d)\s+([A-Za-z]+(?:[ -][A-Za-z]+)*)\s+([A-Za-z0-9]+(?:[ -][A-Za-z0-9]+)*)$'

    match = re.match(descriptionRegex, carDescription)

    if not match: 
        return False 
    
    year = int(match.group(1))
    print(f"The value of year {year}")

    return True if 1980 <= year <= currYear else False 

def displayConfirmationMessage(eventObject): 
    confirmationMsg = f"""
Please confirm your details - 
Name: {eventObject['name']}
Phone: {eventObject['number']}
Email: {eventObject['email']}
Car: {eventObject['carModel']}
Location: {eventObject['location']}
Cleaning: {eventObject['description']}
Time: {eventObject['start'] - eventObject['start'] + timedelta(hour=1)}
    """
    print(confirmationMsg)