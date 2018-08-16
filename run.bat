@ECHO OFF
ECHO Running YrlaLogParser python program.
ECHO Will open a browser tab with results when done.

ECHO Installing packages needed for Google authentication and access.
pip install --upgrade google-api-python-client
pip install --upgrade oauth2client
ECHO Working...
python main.py
ECHO Done!