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
def handle_webhook():
    """Main webhook handler for all Omi events"""
    # Get request data
    data = request.get_json()
    uid = request.args.get('uid')
    key = request.args.get('key')

    # Verify webhook key
    if not verify_key(key):
        response = ('Invalid webhook key', 401)
        log_webhook_event('unknown', uid, data, response)
        return response

    if not data or not uid:
        response = ('Missing required data', 400)
        log_webhook_event('unknown', uid, data, response)
        return response

    try:
        # Handle different event types
        event_type = data.get('type', 'memory_created')

        # Memory Events
        if event_type in MEMORY_EVENTS:
            response = handle_memory_webhook(event_type, data, uid)
        # Audio Events
        elif event_type in AUDIO_EVENTS:
            response = handle_audio_webhook(event_type, data, uid)
        # Transcript Events
        elif event_type in TRANSCRIPT_EVENTS:
            response = handle_transcript_webhook(event_type, data, uid)
        # System Events
        elif event_type in SYSTEM_EVENTS:
            response = handle_system_webhook(event_type, data, uid)
        else:
            response = (jsonify({'error': 'Unknown event type'}), 400)
            log_webhook_event(event_type, uid, data, response)
            return response

        # Log the event and response
        log_level = logging.ERROR if response[1] >= 400 else logging.INFO
        log_webhook_event(event_type, uid, data, response)
        return response

    except Exception as e:
        response = (jsonify({'error': str(e)}), 500)
        log_webhook_event(event_type, uid, data, response)
        return response

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
