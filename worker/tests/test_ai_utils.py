"""
Unit tests for AI utilities
"""
import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.ai import extract_json_from_text


class TestExtractJsonFromText:
    """Test JSON extraction from various text formats"""

    def test_plain_json(self):
        """Test extracting plain JSON"""
        text = '{"primary_colors": ["#FF0000"], "pose": "standing"}'
        result = extract_json_from_text(text)
        assert result is not None
        assert result["primary_colors"] == ["#FF0000"]
        assert result["pose"] == "standing"

    def test_json_with_whitespace(self):
        """Test extracting JSON with extra whitespace"""
        text = '\n\n  {"primary_colors": ["#FF0000"]}  \n'
        result = extract_json_from_text(text)
        assert result is not None
        assert result["primary_colors"] == ["#FF0000"]

    def test_json_in_markdown_code_block(self):
        """Test extracting JSON from markdown code block"""
        text = '''Here's the analysis:
```json
{
  "primary_colors": ["#FF0000", "#0000FF"],
  "pose": "sitting",
  "clothing": "red shirt"
}
```
Hope this helps!'''
        result = extract_json_from_text(text)
        assert result is not None
        assert result["primary_colors"] == ["#FF0000", "#0000FF"]
        assert result["pose"] == "sitting"
        assert result["clothing"] == "red shirt"

    def test_json_in_code_block_without_language(self):
        """Test extracting JSON from code block without language specifier"""
        text = '''```
{"primary_colors": ["#FF0000"]}
```'''
        result = extract_json_from_text(text)
        assert result is not None
        assert result["primary_colors"] == ["#FF0000"]

    def test_json_with_surrounding_text(self):
        """Test extracting JSON with text before and after"""
        text = 'Here is the analysis: {"primary_colors": ["#FF0000"], "pose": "standing"} - end of response'
        result = extract_json_from_text(text)
        assert result is not None
        assert result["primary_colors"] == ["#FF0000"]
        assert result["pose"] == "standing"

    def test_nested_json(self):
        """Test extracting nested JSON objects"""
        text = '''```json
{
  "primary_colors": ["#FF0000"],
  "metadata": {
    "confidence": 0.9,
    "tags": ["person", "standing"]
  }
}
```'''
        result = extract_json_from_text(text)
        assert result is not None
        assert result["primary_colors"] == ["#FF0000"]
        assert result["metadata"]["confidence"] == 0.9
        assert result["metadata"]["tags"] == ["person", "standing"]

    def test_invalid_json(self):
        """Test handling of invalid JSON"""
        text = "This is not JSON at all"
        result = extract_json_from_text(text)
        assert result is None

    def test_malformed_json(self):
        """Test handling of malformed JSON"""
        text = '{"primary_colors": ["#FF0000",}'
        result = extract_json_from_text(text)
        assert result is None

    def test_empty_string(self):
        """Test handling of empty string"""
        text = ""
        result = extract_json_from_text(text)
        assert result is None

    def test_json_array_not_object(self):
        """Test that we correctly handle JSON arrays (should return None as we expect objects)"""
        text = '["#FF0000", "#0000FF"]'
        result = extract_json_from_text(text)
        # Function only extracts objects, not arrays
        assert result is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
