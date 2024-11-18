"""
Omi App Webhook Server - Transcript Event Tests
"""
import requests
from . import WEBHOOK_URL, WEBHOOK_SECRET, add_test_result

def test_transcript_events():
    """Test transcript event handling - success and failure cases"""
    # Test valid transcript segments
    send_test_webhook(
        'valid_segments',
        [
            {
                "text": "Test segment",
                "speaker": "SPEAKER_00",
                "speakerId": 0,
                "is_user": True,
                "start": 0.0,
                "end": 1.0
            }
        ],
        200,
        {"message": "Success"},
        session_id="test-session-1"
    )

    # Test missing session_id
    send_test_webhook(
        'missing_session_id',
        [
            {
                "text": "Test segment",
                "speaker": "SPEAKER_00",
                "speakerId": 0,
                "is_user": True,
                "start": 0.0,
                "end": 1.0
            }
        ],
        400,
        {"error": "Missing session_id parameter"}
    )

    # Test invalid segment format
    send_test_webhook(
        'invalid_segment',
        [
            {
                "text": "Test segment",
                "speaker": "SPEAKER_00",
                # Missing required fields
                "start": 0.0,
                "end": 1.0
            }
        ],
        400,
        {"error": "Missing required field in segment: speakerId"},
        session_id="test-session-1"
    )

    # Test invalid time values
    send_test_webhook(
        'invalid_time_values',
        [
            {
                "text": "Test segment",
                "speaker": "SPEAKER_00",
                "speakerId": 0,
                "is_user": True,
                "start": 2.0,
                "end": 1.0  # End before start
            }
        ],
        400,
        {"error": "start time must be <= end time"},
        session_id="test-session-1"
    )

def send_test_webhook(test_name, data, expected_status, expected_response, session_id=None):
    """Send test webhook and verify response"""
    headers = {'Content-Type': 'application/json'}

    # Build URL with parameters
    url = f"{WEBHOOK_URL}?uid=test-user-1&key={WEBHOOK_SECRET}"
    if session_id:
        url += f"&session_id={session_id}"

    try:
        response = requests.post(
            url,
            json=data,
            headers=headers
        )

        print(f"\nTesting {test_name}:")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")

        success = (
            response.status_code == expected_status and
            response.json() == expected_response
        )

        add_test_result(
            test_name,
            success,
            "Test passed" if success else f"Expected {expected_status} {expected_response}, got {response.status_code} {response.text}"
        )

    except Exception as e:
        add_test_result(
            test_name,
            False,
            f"Request failed: {str(e)}"
        )
