"""
    This file's purpose is to host some helper function(s) for various mini-tasks
"""
from datetime import timedelta

def convertDateTime(dateTimeObject): 
    # this looks like 'September 15, 2024 at 6:00AM'
    formattedTime = dateTimeObject.strftime("%B %d, %Y at %-I:%M %p")

    endTime = dateTimeObject + timedelta(hours=1)
    formattedEndTime = endTime.strftime("%-I:%M %p")

    return f"{formattedTime} - {formattedEndTime}"