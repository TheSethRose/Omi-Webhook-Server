"""
Omi App Webhook Server - Memory Event Tests
"""
import requests
from . import WEBHOOK_URL, WEBHOOK_SECRET, add_test_result

def test_memory_events():
    """Test all memory event types - success and failure cases"""
    # Test memory created (full format from Omi)
    send_test_webhook(
        'memory_created',
        {
            "type": "memory_created",
            "memory": {
                "id": "test-memory-1",
                "created_at": "2024-03-19T12:00:00Z",
                "started_at": "2024-03-19T11:55:00Z",
                "finished_at": "2024-03-19T12:00:00Z",
                "transcript": "Test memory content",
                "transcript_segments": [
                    {
                        "text": "Test memory content",
                        "speaker": "SPEAKER_00",
                        "speakerId": 0,
                        "is_user": True,
                        "start": 0.0,
                        "end": 5.0
                    }
                ],
                "photos": [],
                "structured": {
                    "title": "Test Memory",
                    "overview": "Brief overview",
                    "emoji": "📝",
                    "category": "personal",
                    "action_items": [
                        {
                            "description": "Test action item",
                            "completed": False
                        }
                    ],
                    "events": []
                }
            }
        },
        200,
        {"message": "Memory processed successfully"}
    )

    # Test memory creation failed
    send_test_webhook(
        'new_memory_create_failed',
        {
            "type": "new_memory_create_failed",
            "error": "Test error message"
        },
        200,
        {"message": "Failure logged"}
    )

    # Test new processing memory created
    send_test_webhook(
        'new_processing_memory_created',
        {
            "type": "new_processing_memory_created",
            "memory": {
                "id": "test-memory-2",
                "status": "processing_started"
            }
        },
        200,
        {"message": "Processing memory created"}
    )

    # Test memory processing started
    send_test_webhook(
        'memory_processing_started',
        {
            "type": "memory_processing_started",
            "memory": {
                "id": "test-memory-1",
                "status": "processing"
            }
        },
        200,
        {"message": "Processing started"}
    )

    # Test memory status changed
    send_test_webhook(
        'processing_memory_status_changed',
        {
            "type": "processing_memory_status_changed",
            "memory": {
                "id": "test-memory-1",
                "status": "completed"
            }
        },
        200,
        {"message": "Status updated"}
    )

    # Test memory synced
    send_test_webhook(
        'memory_backward_synced',
        {
            "type": "memory_backward_synced",
            "memory": {
                "id": "test-memory-1",
                "sync_status": "completed"
            }
        },
        200,
        {"message": "Memory synced"}
    )

    # Test missing memory data
    send_test_webhook(
        'memory_created (missing data)',
        {
            "type": "memory_created"
        },
        400,
        {"error": "Missing memory data"}
    )

    # Test invalid memory format
    send_test_webhook(
        'memory_created (invalid memory)',
        {
            "type": "memory_created",
            "memory": {}
        },
        400,
        {"error": "Missing memory data"}
    )

def send_test_webhook(event_type, data, expected_status, expected_response):
    """Send test webhook and verify response"""
    headers = {'Content-Type': 'application/json'}
    url = f"{WEBHOOK_URL}?uid=test-user-1&key={WEBHOOK_SECRET}"

    try:
        response = requests.post(
            url,
            json=data,
            headers=headers
        )

        print(f"\nTesting {event_type}:")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")

        success = (
            response.status_code == expected_status and
            response.json() == expected_response
        )

        add_test_result(
            event_type,
            success,
            "Test passed" if success else f"Expected {expected_status} {expected_response}, got {response.status_code} {response.text}"
        )

    except Exception as e:
        add_test_result(
            event_type,
            False,
            f"Request failed: {str(e)}"
        )
