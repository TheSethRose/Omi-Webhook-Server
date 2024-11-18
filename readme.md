# Omi Webhook Server

A Python server that receives and processes webhook notifications from the [Omi](https://github.com/BasedHardware/omi) app. This server handles real-time memory creation, audio streaming, and transcription events for Omi wearable devices.

## Overview

This webhook server is designed to work with all Omi wearable devices and has been confirmed working with the Dev Kit 1. Omi devices are open-source AI wearables that enable automatic, high-quality transcriptions of meetings, chats, and voice memos. The server implements webhook endpoints that align with Omi's webhook system (`/app/lib/backend/http/webhooks.dart`) to handle:

1. Memory Events (from `message_event.dart`)
   - `memory_created` - New memory creation
   - `new_memory_create_failed` - Failed memory creation
   - `new_processing_memory_created` - Processing memory initiated
   - `memory_processing_started` - Memory processing started
   - `processing_memory_status_changed` - Processing status updates
   - `memory_backward_synced` - Memory sync completed

2. Audio Events
   - `audio_bytes` - Real-time PCM audio streaming from the Dev Kit 1

3. Transcript Events
   - `transcript_segment` - Real-time speech-to-text segments

4. System Events
   - `ping` - Health check endpoint

## Setup

1. Install required Python packages:

```bash
pip install -r requirements.txt
```

2. Create a `.env` file with your configuration:

```bash
# Generate a secret: python -c "import secrets; print(secrets.token_hex(32))"
WEBHOOK_SECRET=your_webhook_secret_here
PORT=32768
```

3. Run the server:

```bash
python server.py
```

## Webhook Configuration in Omi

In the Omi app settings, configure your webhook URL:

```
http://your-server:32768/webhook?key=YOUR_SECRET
```

The Omi app will automatically:

- Add the `uid` parameter to requests
- Send JSON-formatted webhook payloads
- Include `Content-Type: application/json` header

## Event Payloads

1. Memory Event (from `message.dart`):

```json
{
    "type": "memory_created",
    "memory": {
        "id": "memory_id",
        "created_at": "ISO8601_timestamp",
        "text": "memory_content",
        "structured": {
            "title": "memory_title",
            "emoji": "memory_emoji"
        }
    }
}
```

2. Audio Event:

```json
{
    "type": "audio_bytes",
    "audio": "hex_encoded_pcm_audio"
}
```

3. Transcript Event (from `transcript_segment.dart`):

```json
{
    "type": "transcript_segment",
    "segment": {
        "text": "transcribed_text",
        "start_time": 0.0,
        "end_time": 2.5,
        "confidence": 0.95
    }
}
```

## Project Structure

```
omi-webhook/
├── events/                 # Event handlers
│   ├── __init__.py        # Event type exports
│   ├── memory_events.py   # Memory event handlers
│   ├── audio_events.py    # Audio streaming handlers
│   └── transcript_events.py # Transcription handlers
├── tests/                 # Test suites
│   ├��─ __init__.py       # Test utilities
│   ├── test_memory.py    # Memory event tests
│   ├── test_audio.py     # Audio event tests
│   ├── test_system.py    # System event tests
│   └── test_transcript.py # Transcript tests
├── server.py             # Main Flask server
├── test.py              # Test runner
├── requirements.txt     # Python dependencies
└── .env                # Configuration
```

## Testing

1. Run all tests:

```bash
python test.py
```

2. Test individual endpoints:

```bash
# Test ping
curl -X POST "http://localhost:32768/webhook?uid=test-user-1&key=YOUR_SECRET" \
  -H "Content-Type: application/json" \
  -d '{"type":"ping"}'

# Test memory creation
curl -X POST "http://localhost:32768/webhook?uid=test-user-1&key=YOUR_SECRET" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "memory_created",
    "memory": {
      "id": "test-1",
      "created_at": "2024-03-19T12:00:00Z",
      "text": "Test memory"
    }
  }'
```

## Security

1. Authentication:
   - URL key parameter must match WEBHOOK_SECRET
   - Each request must include valid user ID

2. Input Validation:
   - Memory format validation
   - Audio format validation
   - Transcript format validation

3. Error Handling:
   - Invalid requests return 400 status
   - Authentication failures return 401
   - Server errors return 500

## Development

1. Local Testing:

```bash
# Start server
python server.py

# In another terminal
python test.py
```

2. Testing with Omi App:
   - Install ngrok: <https://ngrok.com/download>
   - Start your webhook server: `python server.py`
   - Create tunnel to your server: `ngrok http 32768`
   - Copy the ngrok URL (e.g., `https://abc123.ngrok.io`)
   - Configure in Omi app:

     ```bash
     Webhook URL: https://abc123.ngrok.io/webhook?key=YOUR_SECRET
     ```

   - Omi will automatically append the uid parameter

Note: ngrok is only needed for local development when you want to test with the actual Omi app. For production, you'll want to host the webhook server on a proper server with a static IP/domain.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Run tests: `python test.py`
4. Create a Pull Request

## Special Thanks

Special thanks to [BasedHardware](https://github.com/BasedHardware) for creating the [Omi project](https://github.com/BasedHardware/omi) and making it open source. This webhook server would not be possible without their excellent work on the Omi platform and documentation.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
