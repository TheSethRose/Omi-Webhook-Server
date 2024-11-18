"""
Omi App Webhook Server - Test Utilities
"""
import os
from dotenv import load_dotenv
from typing import Dict, List, Tuple

# Load environment variables
load_dotenv()

WEBHOOK_URL = "http://localhost:32768/webhook"
WEBHOOK_SECRET = os.getenv('WEBHOOK_SECRET')

# Track test results globally
test_results: List[Tuple[str, bool, str]] = []

def add_test_result(test_name: str, success: bool, message: str):
    """Add a test result to the global tracker"""
    test_results.append((test_name, success, message))

def get_test_summary() -> Tuple[int, int, int]:
    """Get summary of test results

    Returns:
        Tuple[int, int, int]: (total, passed, failed)
    """
    total = len(test_results)
    passed = sum(1 for _, success, _ in test_results if success)
    return total, passed, total - passed

def print_test_results():
    """Print summary of all test results"""
    total, passed, failed = get_test_summary()

    print("\n=== Test Summary ===")
    print(f"\nTotal Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")

    if failed > 0:
        print("\nFailed Tests:")
        for test, success, message in test_results:
            if not success:
                print(f"❌ {test}: {message}")
        return False
    else:
        print("\n✅ All tests passed!")
        return True
