"""
Omi App Webhook Server - Audio Event Tests
"""
import requests
import numpy as np
from . import WEBHOOK_URL, WEBHOOK_SECRET, add_test_result

def test_audio_events():
    """Test audio event types - success and failure cases"""
    # Generate 1 second of test audio (sine wave)
    sample_rate = 16000
    duration = 1.0  # seconds
    t = np.linspace(0, duration, int(sample_rate * duration))
    frequency = 440  # Hz (A4 note)
    audio_data = (np.sin(2 * np.pi * frequency * t) * 32767).astype(np.int16)

    # Test 16kHz audio (DevKit1 v1.0.4+ and DevKit2)
    send_test_webhook_raw(
        'audio_16khz',
        audio_data.tobytes(),
        200,
        {"message": "Success"},
        sample_rate=16000
    )

    # Test 8kHz audio (DevKit1 v1.0.2)
    audio_data_8k = audio_data[::2]  # Downsample to 8kHz
    send_test_webhook_raw(
        'audio_8khz',
        audio_data_8k.tobytes(),
        200,
        {"message": "Success"},
        sample_rate=8000
    )

    # Test missing sample_rate parameter
    send_test_webhook_raw(
        'missing_sample_rate',
        audio_data.tobytes(),
        400,
        {"error": "Missing sample_rate parameter"}
    )

    # Test invalid sample rate
    send_test_webhook_raw(
        'invalid_sample_rate',
        audio_data.tobytes(),
        400,
        {"error": "Invalid sample rate. Must be 8000 or 16000"},
        sample_rate=44100
    )

    # Test invalid audio length (odd number of bytes)
    send_test_webhook_raw(
        'invalid_audio_length',
        b'123',  # 3 bytes
        400,
        {"error": "Invalid PCM audio data length"},
        sample_rate=16000,
        codec='pcm'
    )

    # Test empty audio
    send_test_webhook_raw(
        'empty_audio',
        b'',
        400,
        {"error": "Missing audio data"},
        sample_rate=16000
    )

def test_audio_codecs():
    """Test different audio codecs"""
    # Generate test audio
    sample_rate = 16000
    duration = 1.0
    t = np.linspace(0, duration, int(sample_rate * duration))
    frequency = 440
    audio_data = (np.sin(2 * np.pi * frequency * t) * 32767).astype(np.int16)

    # Test PCM audio
    send_test_webhook_raw(
        'pcm_audio',
        audio_data.tobytes(),
        200,
        {"message": "Success"},
        sample_rate=16000,
        codec='pcm'
    )

    # Test Opus audio (simulated)
    send_test_webhook_raw(
        'opus_audio',
        b'opus_data',  # Simulated Opus data
        200,
        {"message": "Success"},
        sample_rate=16000,
        codec='opus'
    )

    # Test invalid codec
    send_test_webhook_raw(
        'invalid_codec',
        audio_data.tobytes(),
        400,
        {"error": "Invalid codec. Must be pcm or opus"},
        sample_rate=16000,
        codec='mp3'
    )

def send_test_webhook_raw(test_name, data, expected_status, expected_response, sample_rate=None, codec=None):
    """Send raw audio test webhook and verify response"""
    headers = {'Content-Type': 'application/octet-stream'}

    # Build URL with parameters
    url = f"{WEBHOOK_URL}?uid=test-user-1&key={WEBHOOK_SECRET}"
    if sample_rate is not None:
        url += f"&sample_rate={sample_rate}"
    if codec is not None:
        url += f"&codec={codec}"

    try:
        response = requests.post(
            url,
            data=data,
            headers=headers
        )

        print(f"\nTesting {test_name}:")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        print(f"Audio size: {len(data)} bytes")

        success = (
            response.status_code == expected_status and
            response.json() == expected_response
        )

        add_test_result(
            test_name,
            success,
            "Test passed" if success else f"Expected {expected_status} {expected_response}, got {response.status_code} {response.text}"
        )

    except Exception as e:
        add_test_result(
            test_name,
            False,
            f"Request failed: {str(e)}"
        )
