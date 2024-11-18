"""
Omi App Webhook Server - Transcript Event Handlers

Handles real-time transcript segments from Omi app's speech-to-text service.
Based on transcript_segment.dart and webhooks.dart
"""
import json
import logging
from flask import jsonify

logger = logging.getLogger(__name__)

# List of transcript event types from message_event.dart
TRANSCRIPT_EVENTS = [
    'transcript_segment'
]

def handle_transcript_webhook(event_type, data, uid):
    """Route transcript events to appropriate handler

    Args:
        event_type (str): Type of transcript event
        data (dict): Webhook payload
        uid (str): User ID from Omi app
    """
    handlers = {
        'transcript_segment': handle_transcript_event
    }

    handler = handlers.get(event_type)
    if not handler:
        return jsonify({'error': 'Unknown transcript event type'}), 400

    return handler(data.get('segment', data), uid)

def handle_transcript_event(segment, uid):
    """Handle real-time transcript segment events

    Args:
        segment (dict): Transcript segment from Omi's speech-to-text
        uid (str): User ID

    Segment format (from transcript_segment.dart):
    {
        "text": str,           # Transcribed text
        "start_time": float,   # Start time in seconds
        "end_time": float,     # End time in seconds
        "confidence": float    # Confidence score 0-1
    }
    """
    # Check for missing data
    if not segment:
        return jsonify({'error': 'Missing segment data'}), 400

    # Validate required fields
    required_fields = ['text', 'start_time', 'end_time', 'confidence']
    if not all(field in segment for field in required_fields):
        return jsonify({'error': 'Invalid segment format'}), 400

    # Validate field types
    try:
        assert isinstance(segment['text'], str), "text must be string"
        assert isinstance(segment['start_time'], (int, float)), "start_time must be numeric"
        assert isinstance(segment['end_time'], (int, float)), "end_time must be numeric"
        assert isinstance(segment['confidence'], (int, float)), "confidence must be numeric"
        assert 0 <= segment['confidence'] <= 1, "confidence must be between 0 and 1"
        assert segment['start_time'] <= segment['end_time'], "start_time must be <= end_time"
    except AssertionError as e:
        return jsonify({'error': f'Invalid segment format: {str(e)}'}), 400

    logger.info(f"Processing transcript segment for user {uid}")
    logger.info(f"Segment data: {json.dumps(segment, indent=2)}")

    # TODO: Add your transcript processing logic here
    # Example: Store in database, real-time analysis, etc.

    return jsonify({'message': 'Success'}), 200
