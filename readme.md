# Omi Webhook Server

A Python server that receives and processes webhook notifications from the [Omi](https://github.com/BasedHardware/omi) app. This server handles real-time memory creation, audio streaming, and transcription events for Omi wearable devices.

## Important Note

This webhook server provides the foundation for receiving events from the Omi app (memory creation, audio streaming, transcripts), but it doesn't include default actions or behaviors for these events. You'll need to implement your own logic for handling these events.

## Installation

### Option 1: Docker (Recommended)

1. Clone this repository
2. Copy the example environment file:

   ```bash
   cp env.example .env
   ```

3. Generate and set your webhook secret:

   ```bash
   python -c "import secrets; print(secrets.token_hex(32))"
   # Add the generated secret to .env
   ```

4. Start the server:

   ```bash
   docker compose up -d
   ```

The server will be available at `http://localhost:32768` with:

- Automatic restarts on failure
- Health monitoring
- Log management
- Dependency handling

Monitor your server:

```bash
docker compose ps    # View status
docker compose logs  # View logs
```

### Option 2: Manual Installation

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment:

   ```bash
   cp env.example .env
   # Edit .env with your settings
   ```

3. Start server:

   ```bash
   python server.py
   ```

## Configuration

### Environment Variables

Key settings in your `.env` file:

```bash
PORT=32768                # Server port
HOST=0.0.0.0             # Server host
WEBHOOK_SECRET=your_key   # Authentication secret
LOG_LEVEL=INFO           # Logging verbosity
LOG_EVENTS=true          # Detailed event logging
```

### Logging Configuration

Two logging controls:

1. `LOG_LEVEL`: General verbosity (INFO, WARNING, ERROR, DEBUG, CRITICAL)
2. `LOG_EVENTS`: Event detail logging (true/false)

Example logs:

```bash
# With LOG_EVENTS=false
2024-03-20 14:23:06 [INFO] memory_created | uid:test-user-1 | status:200

# With LOG_EVENTS=true
2024-03-20 14:23:06 [INFO] memory_created | uid:test-user-1 | status:200 | data:{...} | response:{...}
```

## Usage

### Webhook URL Format

```bash
http://your-server:32768/webhook?key=YOUR_SECRET
```

### Supported Events

1. Memory Events
   - `memory_created`: New memory creation
   - `memory_processing_started`: Processing initiation
   - `processing_memory_status_changed`: Status updates
   - `memory_backward_synced`: Sync completion

2. Audio Events
   - `audio_bytes`: Real-time PCM audio streaming

3. Transcript Events
   - `transcript_segment`: Real-time speech-to-text

4. System Events
   - `ping`: Health check endpoint

### Event Payload Examples

Memory Event:

```json
{
    "type": "memory_created",
    "memory": {
        "id": "memory_id",
        "created_at": "ISO8601_timestamp",
        "text": "memory_content"
    }
}
```

Audio Event:

```json
{
    "type": "audio_bytes",
    "audio": "hex_encoded_pcm_audio"
}
```

Transcript Event:

```json
{
    "type": "transcript_segment",
    "segment": {
        "text": "transcribed_text",
        "start_time": 0.0,
        "end_time": 2.5
    }
}
```

## Development

### Project Structure

```bash
omi-webhook/
├── events/                 # Event handlers
├── tests/                 # Test suites
├── server.py             # Main server
├── test.py              # Test runner
└── .env                # Configuration
```

### Testing

Run tests:

```bash
python test.py
```

### Local Development with Omi App

1. Start server:

   ```bash
   python server.py
   ```

2. Create tunnel (for testing with Omi app):

   ```bash
   ngrok http 32768
   ```

3. Configure in Omi app:

   ```bash
   Webhook URL: https://[ngrok-url]/webhook?key=YOUR_SECRET
   ```

## Docker Details

### Health Checks

- 30-second interval checks
- 3 retries before marking unhealthy
- 5-second startup grace period
- Automatic restart on failure

Monitor health:

```bash
docker ps
# or
docker inspect webhook-server | grep -A 10 Health
```

## Security

- URL key authentication
- User ID validation
- Input format validation
- Proper error status codes (400, 401, 500)

## Contributing

1. Fork repository
2. Create feature branch
3. Run tests
4. Submit pull request

## License

MIT License - see [LICENSE](LICENSE)

## Acknowledgments

Special thanks to [BasedHardware](https://github.com/BasedHardware) for creating the [Omi project](https://github.com/BasedHardware/omi).
