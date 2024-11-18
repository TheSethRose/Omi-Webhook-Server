"""
Omi App Webhook Server - Memory Event Handlers
Handles all memory-related events from message_event.dart
"""
import json
import logging
from flask import jsonify
import os

logger = logging.getLogger('events.memory_events')

# List of memory event types from message_event.dart in Omi App
MEMORY_EVENTS = [
    'memory_created',
    'new_memory_create_failed',
    'new_processing_memory_created',
    'memory_processing_started',
    'processing_memory_status_changed',
    'memory_backward_synced'
]

# Get event logging preference
LOG_EVENTS = os.getenv('LOG_EVENTS', 'false').lower() in ('true', '1', 'yes')

def handle_memory_webhook(event_type, data, uid):
    """Handle memory events from Omi App

    Memory format from Omi:
    {
        "id": str,
        "created_at": "ISO8601_timestamp",
        "started_at": "ISO8601_timestamp",
        "finished_at": "ISO8601_timestamp",
        "transcript": str,
        "transcript_segments": [
            {
                "text": str,
                "speaker": str,
                "speakerId": int,
                "is_user": bool,
                "start": float,
                "end": float
            }
        ],
        "photos": [],
        "structured": {
            "title": str,
            "overview": str,
            "emoji": str,
            "category": str,
            "action_items": [
                {
                    "description": str,
                    "completed": bool
                }
            ],
            "events": []
        }
    }
    """
    handlers = {
        'memory_created': handle_memory_created,
        'new_memory_create_failed': handle_memory_creation_failed,
        'new_processing_memory_created': handle_processing_memory_created,
        'memory_processing_started': handle_memory_processing_started,
        'processing_memory_status_changed': handle_memory_processing_status,
        'memory_backward_synced': handle_memory_synced
    }

    handler = handlers.get(event_type)
    if not handler:
        return jsonify({'error': 'Unknown memory event type'}), 400

    # Check for missing memory data
    if event_type == 'memory_created' and not data.get('memory'):
        return jsonify({'error': 'Missing memory data'}), 400

    return handler(data.get('memory', data), uid)

def handle_memory_created(memory, uid):
    """Handle new memory creation events"""
    if not memory:
        return jsonify({'error': 'Missing memory data'}), 400

    # Validate required memory fields based on Omi format
    required_fields = {
        'id': str,
        'created_at': str,
        'transcript': str,
        'transcript_segments': list,
        'structured': dict
    }

    for field, field_type in required_fields.items():
        if field not in memory:
            return jsonify({'error': f'Missing required field: {field}'}), 400
        if not isinstance(memory[field], field_type):
            return jsonify({'error': f'Invalid type for {field}'}), 400

    # Validate structured data format
    structured_fields = {
        'title': str,
        'overview': str,
        'emoji': str,
        'category': str,
        'action_items': list,
        'events': list
    }

    for field, field_type in structured_fields.items():
        if field not in memory['structured']:
            return jsonify({'error': f'Missing structured field: {field}'}), 400
        if not isinstance(memory['structured'][field], field_type):
            return jsonify({'error': f'Invalid type for structured.{field}'}), 400

    if LOG_EVENTS:
        logger.info(f"Memory created: {json.dumps(memory, indent=2)}")

    return jsonify({'message': 'Memory processed successfully'}), 200

def handle_memory_creation_failed(data, uid):
    """Handle failed memory creation events"""
    if LOG_EVENTS:
        logger.error(f"Memory creation failed for user {uid}")
        logger.error(f"Error data: {json.dumps(data, indent=2)}")
    return jsonify({'message': 'Failure logged'}), 200

def handle_processing_memory_created(data, uid):
    """Handle new processing memory created events"""
    if LOG_EVENTS:
        logger.info(f"New processing memory created for user {uid}")
        logger.info(f"Processing memory: {json.dumps(data, indent=2)}")
    return jsonify({'message': 'Processing memory created'}), 200

def handle_memory_processing_started(data, uid):
    """Handle memory processing started events"""
    if LOG_EVENTS:
        logger.info(f"Memory processing started for user {uid}")
        logger.info(f"Processing data: {json.dumps(data, indent=2)}")
    return jsonify({'message': 'Processing started'}), 200

def handle_memory_processing_status(data, uid):
    """Handle memory processing status change events"""
    if LOG_EVENTS:
        logger.info(f"Memory processing status changed for user {uid}")
        logger.info(f"Status data: {json.dumps(data, indent=2)}")
    return jsonify({'message': 'Status updated'}), 200

def handle_memory_synced(data, uid):
    """Handle memory backward sync events"""
    if LOG_EVENTS:
        logger.info(f"Memory synced for user {uid}")
        logger.info(f"Sync data: {json.dumps(data, indent=2)}")
    return jsonify({'message': 'Memory synced'}), 200
