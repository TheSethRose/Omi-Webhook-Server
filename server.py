"""
Omi App Webhook Server - Main Server Module
"""
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import os
import hmac
import hashlib
import json
import logging
from datetime import datetime
import sys
from pathlib import Path
import signal
import atexit
from logging import StreamHandler
from logging.handlers import RotatingFileHandler

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

# Import event handlers
from events import (
    MEMORY_EVENTS, handle_memory_webhook,
    AUDIO_EVENTS, handle_audio_webhook,
    TRANSCRIPT_EVENTS, handle_transcript_webhook
)

# Load environment variables
load_dotenv()

# Configure basic logging
logging.basicConfig(
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO').upper()),
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Silence Flask's werkzeug logger
logging.getLogger('werkzeug').setLevel(logging.ERROR)

# Create logger
logger = logging.getLogger(__name__)

# Simple LOG_EVENTS check
LOG_EVENTS = os.getenv('LOG_EVENTS', 'false').lower() in ('true', '1', 'yes')

app = Flask(__name__)

# Get config from environment
WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET')
PORT = int(os.getenv('PORT', 32768))

# System event types
SYSTEM_EVENTS = ['ping']

def verify_key(key):
    """Verify webhook key from URL parameter"""
    if not WEBHOOK_SECRET:
        return True

    return hmac.compare_digest(key or '', WEBHOOK_SECRET)

def handle_system_webhook(event_type, data, uid):
    """Handle system events like ping"""
    if event_type == 'ping':
        if LOG_EVENTS:
            logger.info(f"Received ping from user {uid}")
        return jsonify({'message': 'pong'}), 200
    return jsonify({'error': 'Unknown system event'}), 400

def log_webhook_event(event_type, uid, data, response):
    """Simple event logger"""
    status_code = response[1] if isinstance(response, tuple) else 200

    # Only log event details if LOG_EVENTS is true
    if LOG_EVENTS:
        if status_code >= 400:
            logger.info(f"{event_type} | uid:{uid} | status:{status_code} | data:{data} | response:{response}")
        else:
            logger.info(f"{event_type} | uid:{uid} | status:{status_code} | data:{data} | response:{response}")

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming webhooks from Omi App"""
    # Validate webhook key
    webhook_key = request.args.get('key')
    if not webhook_key or webhook_key != WEBHOOK_SECRET:
        return 'Invalid webhook key', 401

    # Get user ID
    uid = request.args.get('uid')
    if not uid:
        return 'Missing uid parameter', 400

    # Get request data
    if request.headers.get('Content-Type') == 'application/octet-stream':
        # Handle audio data
        return handle_audio_webhook(None, None, uid)

    try:
        data = request.get_json()
    except Exception as e:
        return jsonify({'error': 'Invalid JSON data'}), 400

    # Special case: Transcript webhooks send array directly
    if isinstance(data, list):
        # For transcripts, session_id is required in query params
        session_id = request.args.get('session_id')
        if not session_id:
            return jsonify({'error': 'Missing session_id parameter'}), 400
        return handle_transcript_webhook(None, data, uid)

    # For all other webhooks, expect type field
    event_type = data.get('type')
    if not event_type:
        return jsonify({'error': 'Missing event type'}), 400

    # Route to appropriate handler
    if event_type == 'ping':
        logger.info(f"Received ping from user {uid}")
        return jsonify({'message': 'pong'}), 200
    elif event_type in MEMORY_EVENTS:
        return handle_memory_webhook(event_type, data, uid)
    else:
        return jsonify({'error': 'Unknown event type'}), 400

def cleanup():
    """Cleanup function to be called on shutdown"""
    logger.info("Shutting down Omi webhook server...")
    # Add any cleanup code here (close db connections, etc.)

def signal_handler(signum, frame):
    """Handle termination signals"""
    signals = {
        signal.SIGTERM: "SIGTERM",
        signal.SIGINT: "SIGINT",
        signal.SIGHUP: "SIGHUP"
    }
    logger.info(f"Received {signals.get(signum, 'UNKNOWN')} signal")
    cleanup()
    sys.exit(0)

if __name__ == '__main__':
    # Register signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGHUP, signal_handler)

    # Register cleanup function
    atexit.register(cleanup)

    logger.info(f"Starting webhook server on port {PORT}")
    try:
        app.run(host='0.0.0.0', port=PORT)
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        cleanup()
        sys.exit(1)
