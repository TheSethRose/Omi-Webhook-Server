"""
Omi App Webhook Server - Audio Event Handlers
"""
import json
import logging
from flask import jsonify
import os

logger = logging.getLogger('events.audio_events')

# List of audio event types
AUDIO_EVENTS = [
    'audio_bytes'
]

# Get event logging preference
LOG_EVENTS = os.getenv('LOG_EVENTS', 'false').lower() in ('true', '1', 'yes')

def handle_audio_webhook(event_type, data, uid):
    """Route audio events to appropriate handler"""
    handlers = {
        'audio_bytes': handle_audio_event
    }

    handler = handlers.get(event_type)
    if handler:
        return handler(data.get('audio', data), uid)
    return jsonify({'error': 'Unknown audio event type'}), 400

def handle_audio_event(audio, uid):
    """Handle real-time audio byte events"""
    if not audio or isinstance(audio, dict):
        return jsonify({'error': 'Missing audio data'}), 400

    try:
        bytes.fromhex(audio)
    except ValueError:
        return jsonify({'error': 'Invalid audio format'}), 400

    if LOG_EVENTS:
        logger.info(f"Audio received: {len(audio)} bytes")

    return jsonify({'message': 'Success'}), 200
