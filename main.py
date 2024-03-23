import firebase_admin
from firebase_admin import credentials, messaging
from datetime import datetime, timedelta
import pytz
from urllib.request import urlopen
import json

try:
    firebase_admin.get_app()
except ValueError as e:
    cred = credentials.ApplicationDefault()
    firebase_admin.initialize_app(cred)

def daily_event_checker(event, context):
    url = "https://old.online.ntnu.no/api/v1/events/"
    response = urlopen(url)
    data_json = json.loads(response.read())
    
    for event in data_json['results']:
        if event['attendance_event'] is not None:
            event_type = event['event_type']  
            registration_start_str = event['attendance_event']['registration_start']
            title = event['title']
            registration_start = datetime.strptime(registration_start_str, "%Y-%m-%dT%H:%M:%S%z")
            notification_time = registration_start - timedelta(minutes=15)
            
            now = datetime.now(pytz.timezone(registration_start.tzinfo.zone))
            if now <= registration_start and now >= notification_time - timedelta(days=1):
                send_fcm_notification(title, registration_start_str, event_type)  

def send_fcm_notification(title, registration_start_str, event_type):
    registration_start = datetime.strptime(registration_start_str, "%Y-%m-%dT%H:%M:%S%z")
    topic = str(event_type)  
    if topic != '3' or topic !='2' or topic != '1':
        topic = '4'
        
    message = messaging.Message(
        notification=messaging.Notification(
            title='Påmelding starter snart!',
            body=f'Påmelding til {title} starter om 15 minutter.'
        ),
        topic=topic  
    )

    try:
        response = messaging.send(message)
        print(f'Successfully sent message: {response}')
    except Exception as e:
        print(f'Error sending message: {e}')


def send_test_notification(request):
    message = messaging.Message(
        notification=messaging.Notification(
            title='Test',
            body='Test notifikasjon'
        ),
        topic='allUsers'
    )

    try:
        response = messaging.send(message)
        return f'Successfully sent message: {response}'
    except Exception as e:
        return f'Error sending message: {e}'