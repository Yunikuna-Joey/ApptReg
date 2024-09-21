# ApptReg

1) Create a virtual environment [optional] 
    - python -m venv "enter_project_name"
    - (MacOS) to activate the environment source project_name/bin/activate
    - (Windows) to activate the environment project_name/Scripts/activate

2) Packages used [mandatory] [format into a requirements.txt at a later time]
    - pip install -q -U google-generativeai [Gemini Model]
    - pip install python-dotenv [personal pref. used to store keys]
    - pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib [setting up access from service account to Google Calendars]
    - pip install python-dateutil
    - pip install pytz
    - pip install tzdata [used on Windows OS to utilize ZoneInfo]