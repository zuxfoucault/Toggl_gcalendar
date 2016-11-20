from __future__ import print_function
import httplib2

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import datetime

import requests
from requests.auth import HTTPBasicAuth
import time
import json

# Toggl payload parameters
payload = {
    'user_agent': 'agent name',
    'workspace_id': 'id',
    'since': '2016-11-19',
    'until': '2016-11-19',
    'page': '1'}


def get_toggl_data():
    i = 1
    data = []
    while True:
        payload['page'] = i
        response = requests.get('https://toggl.com/reports/api/v2/details', auth=HTTPBasicAuth('API token bind with user name', 'api_token'), params=payload)
        # Get list data
        data = data + response.json()['data']
        if response.json()['total_count'] - 50*i <= 0:
            break
        print(i)
        i += 1
        time.sleep(1)

    return data


try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If these scopes modified, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'app_neame'

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    #home_dir = os.path.expanduser('~')
    #credential_dir = os.path.join(home_dir, '.credentials')
    #if not os.path.exists(credential_dir):
    #    os.makedirs(credential_dir)
    #credential_path = os.path.join(credential_dir,
    #                               'calendar-python-quickstart.json')
    credential_path = './calendar_credential.json'

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def main():
    """Shows basic usage of the Google Calendar API.

    Creates a Google Calendar API service object and outputs a list of the next
    10 events on the user's calendar.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    data = get_toggl_data()

    with open('TogglEvnets.josn', mode='r') as file:
        latestTimestamp = json.load(file)['start']['dateTime']

    # Convert to datetime object; timezone aware
    latestTimestamp = datetime.datetime.strptime(''.join(latestTimestamp.rsplit(\
        ':', 1)), "%Y-%m-%dT%H:%M:%S%z")

    i = 0
    while i < len(data):
        entry_timestemp =  data[i]['start']
        entry_timestemp = datetime.datetime.strptime(''.join(entry_timestemp.rsplit(\
            ':', 1)), "%Y-%m-%dT%H:%M:%S%z")

        if latestTimestamp >= entry_timestemp:
            break

        if data[i]['tags'] != []:
            tag = ' #' + ''.join(data[i]['tags'])
        else:
            tag = ''

        event_list ={
            'summary': data[i]['description'] + tag,
            'location': '',
            'description': '',
            'start': {
                'dateTime': data[i]['start'],
                'timeZone': 'UTC+8:00',
            },
            'end': {
                'dateTime': data[i]['end'],
                'timeZone': 'UTC+8:00',
            }
        }

        event_resp = service.events().insert(calendarId='calendar_id', body=event_list).execute()

        # Mark last timestamp from Toggl synchronized with gCalendar
        if i == 0: # Since list order started from latest timestamp
            with open('TogglEvnets.josn', mode="w") as file:
                json.dump(event_resp, file)

        i += 1

if __name__ == '__main__':
    main()
