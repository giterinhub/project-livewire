import functions_framework
import os
import json
import datetime
from google.cloud import secretmanager
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Environment variables (set these in your Cloud Function deployment)
# PROJECT_ID = os.environ.get('PROJECT_ID') # Automatically available in Cloud Functions
SECRET_ID_CALENDAR_KEY = os.environ.get('SECRET_ID_CALENDAR_KEY', 'GOOGLE_CALENDAR_SERVICE_ACCOUNT_KEY_JSON') # Name of the secret in Secret Manager
DEFAULT_CALENDAR_ID = os.environ.get('GOOGLE_CALENDAR_ID', 'primary') # Calendar ID to interact with

SCOPES = ["https://www.googleapis.com/auth/calendar"]

def get_secret(secret_id):
    """Get secret from Secret Manager."""
    client = secretmanager.SecretManagerServiceClient()
    project_id = os.environ.get('GCP_PROJECT') # Standard env var for project ID in Cloud Functions
    if not project_id:
        # Fallback for local testing if GCP_PROJECT is not set
        # You might need to set this manually or use gcloud config
        try:
            import google.auth
            _, project_id = google.auth.default()
        except Exception:
            # Last resort, should be configured if running locally outside gcloud context
            print("Warning: GCP_PROJECT environment variable not set and google.auth.default() failed. Set PROJECT_ID manually if needed.")
            project_id = "your-gcp-project-id" # Replace if needed for local

    if not project_id:
        raise ValueError("Google Cloud Project ID not found. Set GCP_PROJECT environment variable.")

    name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
    response = client.access_secret_version(request={"name": name})
    return response.payload.data.decode("UTF-8")

@functions_framework.http
def calendar_api_handler(request):
    """HTTP Cloud Function to interact with Google Calendar.
    Actions:
    - 'list_events': GET request, lists upcoming events.
        Params: ?calendarId=xxx&maxResults=yy
    - 'add_event': POST request, adds a new event.
        Body: JSON object with event details (summary, start, end, etc.)
        Params: ?calendarId=xxx
    """
    try:
        service_account_key_json_str = get_secret(SECRET_ID_CALENDAR_KEY)
        service_account_key_dict = json.loads(service_account_key_json_str)
        
        creds = service_account.Credentials.from_service_account_info(
            service_account_key_dict, scopes=SCOPES
        )
        service = build("calendar", "v3", credentials=creds)

    except Exception as e:
        print(f"Error initializing Google Calendar service: {e}")
        return f"Error initializing Google Calendar service: {e}", 500

    action = request.args.get('action')
    calendar_id = request.args.get('calendarId', DEFAULT_CALENDAR_ID)

    if request.method == 'GET' and action == 'list_events':
        try:
            now = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
            max_results = int(request.args.get('maxResults', 10))
            
            events_result = (
                service.events()
                .list(
                    calendarId=calendar_id,
                    timeMin=now,
                    maxResults=max_results,
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )
            events = events_result.get("items", [])

            if not events:
                return json.dumps({"message": "No upcoming events found."}), 200, {'Content-Type': 'application/json'}

            formatted_events = []
            for event in events:
                start = event["start"].get("dateTime", event["start"].get("date"))
                formatted_events.append({"start": start, "summary": event["summary"]})
            
            return json.dumps(formatted_events), 200, {'Content-Type': 'application/json'}

        except HttpError as error:
            print(f"An API error occurred: {error}")
            return f"An API error occurred: {error}", error.resp.status
        except Exception as e:
            print(f"Error listing events: {e}")
            return f"Error listing events: {e}", 500

    elif request.method == 'POST' and action == 'add_event':
        try:
            event_data = request.get_json()
            if not event_data:
                return "Invalid JSON payload for event.", 400

            # Basic validation for required fields (adjust as needed)
            required_fields = ['summary', 'start', 'end']
            if not all(field in event_data for field in required_fields):
                return f"Missing required fields in event data: {', '.join(required_fields)}", 400
            if not isinstance(event_data['start'], dict) or not event_data['start'].get('dateTime'):
                 return "Event 'start' must be an object with a 'dateTime' field (RFC3339).", 400
            if not isinstance(event_data['end'], dict) or not event_data['end'].get('dateTime'):
                 return "Event 'end' must be an object with a 'dateTime' field (RFC3339).", 400


            event = service.events().insert(calendarId=calendar_id, body=event_data).execute()
            return json.dumps({'message': 'Event created.', 'eventId': event.get('id'), 'link': event.get('htmlLink')}), 201, {'Content-Type': 'application/json'}

        except HttpError as error:
            print(f"An API error occurred: {error}")
            error_details = error.content.decode('utf-8') if error.content else str(error)
            try:
                error_json = json.loads(error_details)
                message = error_json.get("error", {}).get("message", "Unknown API error")
            except json.JSONDecodeError:
                message = error_details
            return f"An API error occurred: {message}", error.resp.status
        except Exception as e:
            print(f"Error adding event: {e}")
            return f"Error adding event: {e}", 500
    else:
        return "Invalid request. Specify action ('list_events' with GET, 'add_event' with POST) and ensure correct HTTP method.", 400

if __name__ == '__main__':
    # Example local testing (requires environment variables to be set)
    # You would need to mock 'request' object or run with a local Flask server
    # For example, to test list_events:
    # Set GCP_PROJECT, SECRET_ID_CALENDAR_KEY, GOOGLE_CALENDAR_ID
    # Create a mock request:
    # class MockRequest:
    #     def __init__(self, method, args=None, json_data=None):
    #         self.method = method
    #         self.args = args if args is not None else {}
    #         self._json_data = json_data
    #     def get_json(self, silent=False):
    #         return self._json_data

    # print("Testing list_events...")
    # mock_req_list = MockRequest(method='GET', args={'action': 'list_events'})
    # response_list, status_list, _ = calendar_api_handler(mock_req_list)
    # print(f"Status: {status_list}, Response: {response_list}")

    # print("\nTesting add_event...")
    # mock_event_data = {
    #     "summary": "Test Event from Script",
    #     "description": "This is a test event added via script.",
    #     "start": {"dateTime": (datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(days=1)).isoformat(), "timeZone": "UTC"},
    #     "end": {"dateTime": (datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(days=1, hours=1)).isoformat(), "timeZone": "UTC"}
    # }
    # mock_req_add = MockRequest(method='POST', args={'action': 'add_event'}, json_data=mock_event_data)
    # response_add, status_add, _ = calendar_api_handler(mock_req_add)
    # print(f"Status: {status_add}, Response: {response_add}")
    pass # Keep the main block clean for Cloud Functions deployment
