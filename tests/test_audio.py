"""
Omi App Webhook Server - Audio Event Tests
"""
import requests
from . import WEBHOOK_URL, WEBHOOK_SECRET, add_test_result

def test_audio_events():
    """Test audio event types - success and failure cases"""
    # Success case
    send_test_webhook(
        'audio_bytes',
        {
            "type": "audio_bytes",
            "audio": b"dummy audio data".hex()
        },
        200,
        {"message": "Success"}
    )

    # Failure cases
    send_test_webhook(
        'audio_bytes (missing data)',
        {"type": "audio_bytes"},
        400,
        {"error": "Missing audio data"}
    )

    send_test_webhook(
        'audio_bytes (invalid format)',
        {"type": "audio_bytes", "audio": "invalid"},
        400,
        {"error": "Invalid audio format"}
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
