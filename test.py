"""
Omi App Webhook Server - Main Test Runner
"""
import sys
from tests import print_test_results
from tests.test_memory import test_memory_events
from tests.test_audio import test_audio_events
from tests.test_transcript import test_transcript_events
from tests.test_system import test_system_events, test_authentication

def run_all_tests():
    """Run all test suites"""
    print("Starting webhook tests...")

    # Run all test suites
    test_authentication()
    test_memory_events()
    test_audio_events()
    test_transcript_events()
    test_system_events()

    # Print results and exit with appropriate code
    success = print_test_results()
    sys.exit(0 if success else 1)

if __name__ == '__main__':
    run_all_tests()
