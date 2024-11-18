"""
Omi App Webhook Server - System Event Tests
"""
import requests
from . import WEBHOOK_URL, WEBHOOK_SECRET, add_test_result

def test_system_events():
    """Test system event types - success and failure cases"""
    # Success case
    send_test_webhook('ping', {"type": "ping"}, 200, {"message": "pong"})

    # Failure case
    send_test_webhook(
        'unknown_event',
        {"type": "unknown_event"},
        400,
        {"error": "Unknown event type"}
    )

def test_authentication():
    """Test authentication cases"""
    headers = {'Content-Type': 'application/json'}

    # Test valid key
    response = requests.post(
        f"{WEBHOOK_URL}?uid=test-user-1&key={WEBHOOK_SECRET}",
        json={"type": "ping"},
        headers=headers
    )
    add_test_result(
        'auth (valid key)',
        response.status_code == 200,
        f"Expected 200, got {response.status_code}"
    )

    # Test missing key
    response = requests.post(
        f"{WEBHOOK_URL}?uid=test-user-1",
        json={"type": "ping"},
        headers=headers
    )
    add_test_result(
        'auth (missing key)',
        response.status_code == 401,
        f"Expected 401, got {response.status_code}"
    )

    # Test invalid key
    response = requests.post(
        f"{WEBHOOK_URL}?uid=test-user-1&key=invalid",
        json={"type": "ping"},
        headers=headers
    )
    add_test_result(
        'auth (invalid key)',
        response.status_code == 401,
        f"Expected 401, got {response.status_code}"
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
