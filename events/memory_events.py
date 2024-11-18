"""
Omi App Webhook Server - Memory Event Handlers
Handles all memory-related events from message_event.dart
"""
import json
import logging
from flask import jsonify

logger = logging.getLogger(__name__)

# List of memory event types from message_event.dart
MEMORY_EVENTS = [
    'memory_created',
    'new_memory_create_failed',
    'new_processing_memory_created',
    'memory_processing_started',
    'processing_memory_status_changed',
    'memory_backward_synced'
]

def handle_memory_webhook(event_type, data, uid):
    """Route memory events to appropriate handler"""
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
    """Handle new memory creation events

    Args:
        memory (dict): Memory data from Omi
        uid (str): User ID

    Memory format:
    {
        "id": str,
        "created_at": str (ISO8601),
        "text": str,
        "structured": {
            "title": str,
            "emoji": str
        }
    }
    """
    if not memory:
        return jsonify({'error': 'Missing memory data'}), 400

    logger.info(f"Processing new memory for user {uid}")
    logger.info(f"Memory data: {json.dumps(memory, indent=2)}")

    # TODO: Add your memory processing logic here
    return jsonify({'message': 'Memory processed successfully'}), 200

def handle_memory_creation_failed(data, uid):
    """Handle failed memory creation events"""
    logger.error(f"Memory creation failed for user {uid}")
    logger.error(f"Error data: {json.dumps(data, indent=2)}")
    return jsonify({'message': 'Failure logged'}), 200

def handle_processing_memory_created(data, uid):
    """Handle new processing memory created events"""
    logger.info(f"New processing memory created for user {uid}")
    logger.info(f"Processing memory: {json.dumps(data, indent=2)}")
    return jsonify({'message': 'Processing memory created'}), 200

def handle_memory_processing_started(data, uid):
    """Handle memory processing started events"""
    logger.info(f"Memory processing started for user {uid}")
    logger.info(f"Processing data: {json.dumps(data, indent=2)}")
    return jsonify({'message': 'Processing started'}), 200

def handle_memory_processing_status(data, uid):
    """Handle memory processing status change events"""
    logger.info(f"Memory processing status changed for user {uid}")
    logger.info(f"Status data: {json.dumps(data, indent=2)}")
    return jsonify({'message': 'Status updated'}), 200

def handle_memory_synced(data, uid):
    """Handle memory backward sync events"""
    logger.info(f"Memory synced for user {uid}")
    logger.info(f"Sync data: {json.dumps(data, indent=2)}")
    return jsonify({'message': 'Memory synced'}), 200