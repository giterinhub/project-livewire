import json
import os
from datetime import datetime

# Placeholder for actual calendar API integration
def create_calendar_entry_in_api(date, time, title, description, attendees=None):
    """
    Placeholder function to simulate creating a calendar entry.
    Replace this with actual API calls to Google Calendar, Outlook, etc.
    Returns the ID of the created event, or None if failed.
    """
    print(f"Simulating creation of calendar entry:")
    print(f"  Date: {date}")
    print(f"  Time: {time}")
    print(f"  Title: {title}")
    print(f"  Description: {description}")
    print(f"  Attendees: {attendees if attendees else 'None'}")
    # Simulate a successful creation with a dummy event ID
    return f"evt_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"


def create_calendar_entry(request):
    """Responds to an HTTP request to create a calendar entry."""
    if request.method != 'POST':
        return 'Only POST requests are accepted', 405

    try:
        request_json = request.get_json(silent=True)
        if not request_json:
            return "Invalid JSON payload", 400
    except Exception as e:
        return f"Error parsing JSON: {e}", 400

    # Get parameters from request JSON body
    # Expected parameters: 'date' (YYYY-MM-DD), 'time' (HH:MM AM/PM or HH:MM), 'title', 'description'
    # Optional: 'attendees' (list of email addresses)
    date_str = request_json.get('date')
    time_str = request_json.get('time')
    title = request_json.get('title')
    description = request_json.get('description')
    attendees = request_json.get('attendees') # Optional

    if not all([date_str, time_str, title, description]):
        return "Missing required parameters: 'date', 'time', 'title', 'description'.", 400

    try:
        # Validate date and time formats (optional, but good practice)
        datetime.strptime(date_str, "%Y-%m-%d")
        # Add more robust time parsing if needed, e.g., supporting 24-hour format
        datetime.strptime(time_str, "%I:%M %p") # Example: "02:30 PM"
    except ValueError:
        return "Invalid date or time format. Use YYYY-MM-DD for date and HH:MM AM/PM for time.", 400

    try:
        # In a real scenario, you'd call your calendar API here
        event_id = create_calendar_entry_in_api(date_str, time_str, title, description, attendees)

        if event_id:
            response_data = {
                "message": "Calendar entry created successfully.",
                "eventId": event_id,
                "details": {
                    "date": date_str,
                    "time": time_str,
                    "title": title,
                    "description": description,
                    "attendees": attendees
                }
            }
            return json.dumps(response_data), 201, {'Content-Type': 'application/json'}
        else:
            return "Failed to create calendar entry via API.", 500

    except Exception as e:
        # Log the error for debugging
        print(f"Error in create_calendar_entry: {e}") # Or use proper logging
        return f"An unexpected error occurred: {e}", 500

if __name__ == '__main__':
    # Example of local testing (optional)
    class MockRequest:
        def __init__(self, json_data, method='POST'):
            self.json_data = json_data
            self.method = method

        def get_json(self, silent=False):
            return self.json_data

    # Test case 1: Successful creation
    payload_success = {
        'date': '2025-12-26',
        'time': '03:00 PM',
        'title': 'Project Brainstorm',
        'description': 'Brainstorm new features for Q1 2026.',
        'attendees': ['alice@example.com', 'bob@example.com']
    }
    mock_request_success = MockRequest(payload_success)
    response_success, status_success, _ = create_calendar_entry(mock_request_success)
    print(f"Create entry - Success (Status: {status_success}):")
    print(response_success)

    # Test case 2: Missing parameters
    payload_missing = {
        'date': '2025-12-27',
        'title': 'Quick Sync'
        # time and description are missing
    }
    mock_request_missing = MockRequest(payload_missing)
    response_missing, status_missing, _ = create_calendar_entry(mock_request_missing)
    print(f"\nCreate entry - Missing params (Status: {status_missing}):")
    print(response_missing)

    # Test case 3: Invalid date format
    payload_invalid_date = {
        'date': '27-12-2025', # Invalid format
        'time': '10:00 AM',
        'title': 'Invalid Date Test',
        'description': 'Testing invalid date format.'
    }
    mock_request_invalid_date = MockRequest(payload_invalid_date)
    response_invalid_date, status_invalid_date, _ = create_calendar_entry(mock_request_invalid_date)
    print(f"\nCreate entry - Invalid date (Status: {status_invalid_date}):")
    print(response_invalid_date)

    # Test case 4: Non-POST request
    mock_request_get = MockRequest({}, method='GET')
    response_get, status_get, _ = create_calendar_entry(mock_request_get)
    print(f"\nCreate entry - GET request (Status: {status_get}):")
    print(response_get)
