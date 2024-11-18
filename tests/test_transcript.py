"""
Omi App Webhook Server - Transcript Event Tests
"""
import requests
from . import WEBHOOK_URL, WEBHOOK_SECRET, add_test_result

def test_transcript_events():
    """Test transcript event types - success and failure cases"""
    # Success case
    send_test_webhook(
        'transcript_segment',
        {
            "type": "transcript_segment",
            "segment": {
                "text": "This is a test transcript",
                "start_time": 0.0,
                "end_time": 2.5,
                "confidence": 0.95
            }
        },
        200,
        {"message": "Success"}
    )

    # Failure cases
    send_test_webhook(
        'transcript_segment (missing data)',
        {"type": "transcript_segment"},
        400,
        {"error": "Invalid segment format"}
    )

    send_test_webhook(
        'transcript_segment (invalid format)',
        {"type": "transcript_segment", "segment": {"text": ""}},
        400,
        {"error": "Invalid segment format"}
    )

def send_test_webhook(event_type, data, expected_status, expected_response):
    """Send test webhook and verify response"""
    headers = {'Content-Type': 'application/json'}

    try:
        response = requests.post(
            f"{WEBHOOK_URL}?uid=test-user-1&key={WEBHOOK_SECRET}",
            json=data,
            headers=headers
        )

        print(f"\nTesting {event_type}:")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")

        # Verify response
        status_matches = response.status_code == expected_status
        content_matches = True

        if expected_response:
            try:
                response_json = response.json()
                content_matches = all(
                    response_json.get(k) == v
                    for k, v in expected_response.items()
                )
            except:
                content_matches = False

        success = status_matches and content_matches
        message = []
        if not status_matches:
            message.append(f"Expected status {expected_status}, got {response.status_code}")
        if not content_matches:
            message.append(f"Response content didn't match expected: {expected_response}")

        add_test_result(
            event_type,
            success,
            " AND ".join(message) if message else "Test passed"
        )

    except Exception as e:
        add_test_result(
            event_type,
            False,
            f"Request failed: {str(e)}"
        )
