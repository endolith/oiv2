#!/usr/bin/env python3
import sys

def test():
    tests = []
    
    try: from structured import TaggedResponse; tests.append("✅ structured")
    except: tests.append("❌ structured")
    
    try: from tools.screen import screenshot; tests.append("✅ screen") 
    except: tests.append("❌ screen")
    
    try: from tools.input import click_grid; tests.append("✅ input")
    except: tests.append("❌ input")
    
    try: from tools.jupyter import python_exec; tests.append("✅ jupyter")
    except: tests.append("❌ jupyter")
    
    try: from tools.files import ls; tests.append("✅ files")
    except: tests.append("❌ files")
    
    # Test XML parsing
    try:
        resp = TaggedResponse("<thinking>test</thinking><message>hello</message><tool_name>test</tool_name><tool_args>{}</tool_args>")
        if resp.reasoning and resp.message and resp.tool_call: tests.append("✅ XML parsing")
        else: tests.append("❌ XML parsing")
    except: tests.append("❌ XML parsing")
    
    # Test system detection
    try:
        from tools.screen import screen
        tests.append(f"✅ system: {screen.sys}")
    except: tests.append("❌ system detection")
    
    passed = len([t for t in tests if t.startswith("✅")])
    total = len(tests)
    
    print(f"🧪 Tests: {passed}/{total}")
    for t in tests: print(f"  {t}")
    
    if passed == total: print("🎉 All tests passed!")
    else: print("⚠️  Some tests failed - check setup")
    
    return passed == total

if __name__ == "__main__": sys.exit(0 if test() else 1)