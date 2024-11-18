"""
Omi App Webhook Server - Memory Event Tests
"""
import requests
from . import WEBHOOK_URL, WEBHOOK_SECRET, add_test_result

def test_memory_events():
    """Test all memory event types - success and failure cases"""
    # Success cases
    memory_events = [
        ('memory_created', {
            "type": "memory_created",
            "memory": {
                "id": "test-memory-1",
                "created_at": "2024-03-19T12:00:00Z",
                "text": "Test memory content",
                "structured": {
                    "title": "Test Memory",
                    "emoji": "📝"
                }
            }
        }, 200, {"message": "Memory processed successfully"}),
        ('new_memory_create_failed', {
            "type": "new_memory_create_failed",
            "error": "Test error message"
        }, 200, {"message": "Failure logged"}),
        ('new_processing_memory_created', {
            "type": "new_processing_memory_created",
            "memory": {
                "id": "test-memory-2",
                "status": "processing_started"
            }
        }, 200, {"message": "Processing memory created"}),
        ('memory_processing_started', {
            "type": "memory_processing_started",
            "memory": {
                "id": "test-memory-1",
                "status": "processing"
            }
        }, 200, {"message": "Processing started"}),
        ('processing_memory_status_changed', {
            "type": "processing_memory_status_changed",
            "memory": {
                "id": "test-memory-1",
                "status": "completed"
            }
        }, 200, {"message": "Status updated"}),
        ('memory_backward_synced', {
            "type": "memory_backward_synced",
            "memory": {
                "id": "test-memory-1",
                "sync_status": "completed"
            }
        }, 200, {"message": "Memory synced"})
    ]

    # Test success cases
    for event_type, data, status, response in memory_events:
        send_test_webhook(event_type, data, status, response)

    # Test failure cases
    send_test_webhook(
        'memory_created (missing data)',
        {"type": "memory_created"},
        400,
        {"error": "Missing memory data"}
    )

    send_test_webhook(
        'memory_created (invalid memory)',
        {"type": "memory_created", "memory": {}},
        400,
        {"error": "Missing memory data"}
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
