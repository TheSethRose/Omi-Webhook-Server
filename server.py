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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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
        logger.info(f"Received ping from user {uid}")
        return jsonify({'message': 'pong'}), 200
    return jsonify({'error': 'Unknown system event'}), 400

@app.route('/webhook', methods=['POST'])
def handle_webhook():
    """Main webhook handler for all Omi events"""

    # Get request data
    data = request.get_json()
    uid = request.args.get('uid')
    key = request.args.get('key')

    # Verify webhook key
    if not verify_key(key):
        return 'Invalid webhook key', 401

    if not data or not uid:
        return 'Missing required data', 400

    # Log the webhook event
    logger.info(f"Received webhook from user {uid}")

    try:
        # Handle different event types
        event_type = data.get('type', 'memory_created')

        # Memory Events
        if event_type in MEMORY_EVENTS:
            return handle_memory_webhook(event_type, data, uid)

        # Audio Events
        elif event_type in AUDIO_EVENTS:
            return handle_audio_webhook(event_type, data, uid)

        # Transcript Events
        elif event_type in TRANSCRIPT_EVENTS:
            return handle_transcript_webhook(event_type, data, uid)

        # System Events
        elif event_type in SYSTEM_EVENTS:
            return handle_system_webhook(event_type, data, uid)

        else:
            logger.warning(f"Unknown event type: {event_type}")
            return jsonify({'error': 'Unknown event type'}), 400

    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return jsonify({'error': str(e)}), 500

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
