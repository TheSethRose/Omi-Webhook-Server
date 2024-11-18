"""
Omi App Webhook Server - Audio Event Handlers

Handles real-time audio streaming from Omi app's DevKit1 and DevKit2 devices.
Based on Omi's audio streaming protocol.
"""
import json
import logging
from flask import jsonify, request
import os

logger = logging.getLogger('events.audio_events')

# List of audio event types
AUDIO_EVENTS = []  # No event types needed - Omi sends raw audio

# Get event logging preference
LOG_EVENTS = os.getenv('LOG_EVENTS', 'false').lower() in ('true', '1', 'yes')

def handle_audio_webhook(event_type, data, uid):
    """Handle audio streaming from Omi App"""
    # Get sample rate and codec from query params
    sample_rate = request.args.get('sample_rate')
    codec = request.args.get('codec', 'pcm')  # Default to PCM if not specified

    if not sample_rate:
        return jsonify({'error': 'Missing sample_rate parameter'}), 400

    try:
        sample_rate = int(sample_rate)
    except ValueError:
        return jsonify({'error': 'Invalid sample rate format'}), 400

    # Validate sample rate
    if sample_rate not in [8000, 16000]:
        return jsonify({'error': 'Invalid sample rate. Must be 8000 or 16000'}), 400

    # Validate codec
    if codec not in ['pcm', 'opus']:
        return jsonify({'error': 'Invalid codec. Must be pcm or opus'}), 400

    # Get raw audio bytes from request body
    audio_bytes = request.get_data()

    if not audio_bytes:
        return jsonify({'error': 'Missing audio data'}), 400

    # Only validate even length for PCM
    if codec == 'pcm' and len(audio_bytes) % 2 != 0:
        return jsonify({'error': 'Invalid PCM audio data length'}), 400

    if LOG_EVENTS:
        logger.info(f"Received {len(audio_bytes)} bytes of {sample_rate}Hz {codec} audio from user {uid}")

    return jsonify({'message': 'Success'}), 200
