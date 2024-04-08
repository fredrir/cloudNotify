import firebase_admin
from firebase_admin import credentials, messaging
from datetime import datetime, timedelta
import pytz
from urllib.request import urlopen
import json
from flask import jsonify

# Cloud function for sending out automatic notifications for Online the App
try:
    firebase_admin.get_app()
except ValueError as e:
    cred = credentials.ApplicationDefault()
    firebase_admin.initialize_app(cred)

def fetch_events(page_url):
    response = urlopen(page_url)
    data_json = json.loads(response.read())
    return data_json['results']

def process_event(event):
    if event['attendance_event'] is not None:
        event_type = event['event_type']
        registration_start_str = event['attendance_event']['registration_start']
        title = event['title']
        registration_start = datetime.strptime(registration_start_str, "%Y-%m-%dT%H:%M:%S%z")
        notification_time = registration_start - timedelta(minutes=15)
        
        now = datetime.now(pytz.utc).astimezone(registration_start.tzinfo)
        if now <= registration_start and now >= notification_time - timedelta(days=1):
            send_fcm_notification(title, registration_start_str, event_type)
    


def daily_event_checker(request):
    base_url = "https://old.online.ntnu.no/api/v1/events/?page="
    pages = [1, 2] 
    all_events_processed = True

    for page in pages:
        page_url = base_url + str(page)
        try:
            events = fetch_events(page_url)
            for event in events:
                process_event(event)
        except Exception as e:
            print(f"Failed to process events from {page_url}: {e}")
            all_events_processed = False

    if all_events_processed:
        return jsonify({"message": "All events processed successfully"}), 200
    else:
        return jsonify({"message": "Some events could not be processed correctly"}),

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
        return f'Successfully sent message: {response}'
    except Exception as e:
        return f'Error sending message: {e}'
    

daily_event_checker('s')