"""
Simple manual test for JSON extraction (no dependencies needed)
Run with: python3 test_json_extraction.py
"""
import json
import re
from typing import Dict, Optional


def extract_json_from_text(text: str) -> Optional[Dict]:
    """
    Extract JSON from text that may contain markdown code blocks or extra text
    """
    # Try to find JSON in markdown code blocks first
    json_pattern = r'```(?:json)?\s*(\{.*?\})\s*```'
    match = re.search(json_pattern, text, re.DOTALL)

    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    # Try to find raw JSON object in the text
    json_pattern = r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}'
    match = re.search(json_pattern, text, re.DOTALL)

    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    # Try parsing the entire text as JSON
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass

    return None


def test_extract_json():
    """Test various JSON extraction scenarios"""

    tests = [
        {
            "name": "Plain JSON",
            "input": '{"primary_colors": ["#FF0000"], "pose": "standing"}',
            "expected_keys": ["primary_colors", "pose"]
        },
        {
            "name": "JSON in markdown code block",
            "input": '''```json
{
  "primary_colors": ["#FF0000", "#0000FF"],
  "pose": "sitting"
}
```''',
            "expected_keys": ["primary_colors", "pose"]
        },
        {
            "name": "JSON with surrounding text",
            "input": 'Here is the analysis: {"primary_colors": ["#FF0000"]} - done',
            "expected_keys": ["primary_colors"]
        },
        {
            "name": "Invalid JSON",
            "input": "This is not JSON at all",
            "expected_keys": None  # Should return None
        },
        {
            "name": "Empty string",
            "input": "",
            "expected_keys": None
        },
        {
            "name": "Nested JSON",
            "input": '{"primary_colors": ["#FF0000"], "metadata": {"confidence": 0.9}}',
            "expected_keys": ["primary_colors", "metadata"]
        }
    ]

    passed = 0
    failed = 0

    for test in tests:
        result = extract_json_from_text(test["input"])

        if test["expected_keys"] is None:
            # Expect None result
            if result is None:
                print(f"✓ PASS: {test['name']}")
                passed += 1
            else:
                print(f"✗ FAIL: {test['name']} - Expected None, got {result}")
                failed += 1
        else:
            # Expect valid JSON with keys
            if result and all(key in result for key in test["expected_keys"]):
                print(f"✓ PASS: {test['name']}")
                passed += 1
            else:
                print(f"✗ FAIL: {test['name']} - Expected keys {test['expected_keys']}, got {result}")
                failed += 1

    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed")
    print(f"{'='*50}")

    return failed == 0


if __name__ == "__main__":
    import sys
    success = test_extract_json()
    sys.exit(0 if success else 1)
