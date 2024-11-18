"""
Omi App Webhook Server - Transcript Event Handlers
"""
import json
import logging
from flask import jsonify, request
import os

logger = logging.getLogger('events.transcript_events')

TRANSCRIPT_EVENTS = []  # No event types needed since we handle it directly

LOG_EVENTS = os.getenv('LOG_EVENTS', 'false').lower() in ('true', '1', 'yes')

def handle_transcript_webhook(event_type, data, uid):
    """Handle transcript segments from Omi App

    Receives array of segments directly in request body:
    [
        {
            "text": "Segment text",
            "speaker": "SPEAKER_00",
            "speakerId": 0,
            "is_user": false,
            "start": 10.0,
            "end": 20.0
        }
        // More segments...
    ]
    """
    # Get session_id from query params as documented
    session_id = request.args.get('session_id')
    if not session_id:
        return jsonify({'error': 'Missing session_id parameter'}), 400

    # Data should be array of segments
    if not isinstance(data, list):
        return jsonify({'error': 'Invalid format - expected array of segments'}), 400

    # Validate each segment
    for segment in data:
        # Check required fields exist
        required_fields = ['text', 'speaker', 'speakerId', 'is_user', 'start', 'end']
        for field in required_fields:
            if field not in segment:
                return jsonify({'error': f'Missing required field in segment: {field}'}), 400

        # Validate field types
        if not isinstance(segment['text'], str):
            return jsonify({'error': 'text must be string'}), 400

        if not isinstance(segment['speaker'], str):
            return jsonify({'error': 'speaker must be string'}), 400

        if not isinstance(segment['speakerId'], int):
            return jsonify({'error': 'speakerId must be integer'}), 400

        if not isinstance(segment['is_user'], bool):
            return jsonify({'error': 'is_user must be boolean'}), 400

        if not (isinstance(segment['start'], (int, float)) and isinstance(segment['end'], (int, float))):
            return jsonify({'error': 'start and end must be numbers'}), 400

        # Validate time values
        if segment['start'] > segment['end']:
            return jsonify({'error': 'start time must be <= end time'}), 400

    if LOG_EVENTS:
        logger.info(f"Received {len(data)} segments for session {session_id}")
        logger.info(f"Segments: {json.dumps(data, indent=2)}")

    return jsonify({'message': 'Success'}), 200
