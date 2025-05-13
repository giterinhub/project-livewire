# Calendar Tools

This directory contains Cloud Functions for interacting with a calendar service.

## Tools

### Get Calendar Tool (`get-calendar-tool/`)
- **Purpose**: Fetches existing calendar entries for a specified date or date range.
- **Trigger**: HTTP GET request.
- **Parameters**:
    - `date` (string, required): The start date for fetching entries, in `YYYY-MM-DD` format.
    - `days` (integer, optional, default: `1`): The number of days (including the start date) for which to fetch entries.
- **Returns**: A JSON array of calendar entries or an error message.

### Create Calendar Tool (`create-calendar-tool/`)
- **Purpose**: Creates a new entry in the calendar.
- **Trigger**: HTTP POST request.
- **Request Body (JSON)**:
    - `date` (string, required): The date of the event, in `YYYY-MM-DD` format.
    - `time` (string, required): The time of the event, in `HH:MM AM/PM` format (e.g., "02:30 PM").
    - `title` (string, required): The title or name of the event.
    - `description` (string, required): A description of the event.
    - `attendees` (list of strings, optional): A list of email addresses for attendees.
- **Returns**: A JSON object confirming the creation and including the event ID, or an error message.

## Setup

1.  **API Integration**:
    *   Modify `get-calendar-tool/main.py` and `create-calendar-tool/main.py` to integrate with your chosen calendar API (e.g., Google Calendar API, Microsoft Graph API for Outlook Calendar).
    *   Replace the placeholder functions (`get_calendar_entries_from_api` and `create_calendar_entry_in_api`) with actual API calls.
2.  **Dependencies**:
    *   Add any necessary Python client libraries for your calendar API to the respective `requirements.txt` files (e.g., `google-api-python-client`).
3.  **Authentication & Authorization**:
    *   Securely manage API keys, OAuth credentials, or service account keys. Consider using Google Cloud Secret Manager for storing sensitive information, similar to how `OPENWEATHER_API_KEY` is handled in the `get-weather-tool`.
    *   Ensure the Cloud Function's service account has the necessary permissions to access and modify calendar data.
4.  **Deployment**:
    *   Deploy each function to Google Cloud Functions. Make sure to set any required environment variables (e.g., `PROJECT_ID`, API keys if not using Secret Manager directly in the function).
    *   Note the trigger URLs for each deployed function.

## Server Configuration

After deploying the Cloud Functions, update the `CLOUD_FUNCTIONS` dictionary in `server/config/config.py` on your main application server to include the URLs for these new tools:

```python
# server/config/config.py
CLOUD_FUNCTIONS = {
    "get_weather": "YOUR_GET_WEATHER_FUNCTION_URL",
    "get_calendar_entries": "YOUR_GET_CALENDAR_ENTRIES_FUNCTION_URL",
    "create_calendar_entry": "YOUR_CREATE_CALENDAR_ENTRY_FUNCTION_URL",
    # ... other tools
}
```

## System Instructions

Update the `server/config/system-instructions.txt` file to inform the AI model about the new calendar tools:

```
You have the following tools available to you:
- get_weather: Get current weather information for a city
- get_calendar_entries: Get calendar entries for a specified date. Parameters: "date" (YYYY-MM-DD), "days" (optional, number of days).
- create_calendar_entry: Create a new calendar entry. Parameters: "date" (YYYY-MM-DD), "time" (HH:MM AM/PM), "title", "description", "attendees" (optional list of emails).
```
