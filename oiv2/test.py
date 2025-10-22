#!/usr/bin/env python3
import sys
import os

def test():
    """Run basic tests for oiv2 functionality."""
    print("🧪 Running oiv2 tests...")

    # Test 1: Check if main modules can be imported
    try:
        from oiv2 import cli, oi, conversation
        print("✅ Core modules import successfully")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

    # Test 2: Check if tools can be imported
    try:
        from oiv2.tools import files, terminal, screen
        print("✅ Tool modules import successfully")
    except ImportError as e:
        print(f"❌ Tool import error: {e}")
        return False

    # Test 3: Check if pyautogui is available (for screen automation)
    try:
        import pyautogui
        print("✅ pyautogui available for screen automation")
    except ImportError:
        print("⚠️  pyautogui not available - screen automation may not work")

    # Test 4: Check if litellm is available (for AI functionality)
    try:
        import litellm
        print("✅ litellm available for AI functionality")
    except ImportError:
        print("❌ litellm not available - AI functionality will not work")
        return False

    print("🎉 All tests passed!")
    return True

if __name__ == "__main__":
    success = test()
    sys.exit(0 if success else 1)
