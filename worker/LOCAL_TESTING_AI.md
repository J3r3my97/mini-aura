# Local AI Integration Testing

This guide shows how to test the AI functions locally before deploying, which saves ~10 minutes per iteration.

## Setup

1. **Install dependencies:**
   ```bash
   pip3 install anthropic pillow --break-system-packages
   # or use a virtual environment:
   python3 -m venv venv
   source venv/bin/activate
   pip install anthropic pillow
   ```

2. **Set environment variables:**
   ```bash
   export CLAUDE_API_KEY="your-anthropic-api-key-here"
   export PROJECT_ID="mini-aura"
   export REGION="us-central1"
   ```

## Run Tests

```bash
cd worker
python3 test_ai_integration.py
```

## What Gets Tested

✅ **JSON Extraction** - Verifies Claude responses can be parsed (with/without markdown)
✅ **Claude Image Analysis** - Tests actual Claude API call with vision model
✅ **Claude Prompt Generation** - Tests prompt creation for Imagen
✅ **Imagen API Parameters** - Validates we're using correct parameters (mocked, no GCP needed)

## Why This Helps

- **Catches API parameter errors** before deployment
- **Tests Claude integration** with real API calls
- **Validates JSON parsing** with various response formats
- **No GCP deployment needed** - runs locally in seconds

## Expected Output

```
============================================================
🧪 AI Integration Tests
============================================================

📝 Testing JSON extraction...
  ✓ Plain JSON: PASS
  ✓ Markdown: PASS
  ✓ With text: PASS

🖼️  Testing Claude image analysis...
  ✓ Analysis successful
    Primary colors: ['#FF0000']
    Pose: solid red square
    ...

✍️  Testing Imagen prompt generation...
  ✓ Prompt generated successfully
    Length: 87 chars
    Preview: ...

🎨 Testing Imagen API call parameters...
  ✓ Imagen API call parameters valid
    Parameters: ['prompt', 'number_of_images']

============================================================
📊 Results Summary
============================================================
✅ PASS: JSON Extraction
✅ PASS: Claude Image Analysis
✅ PASS: Claude Prompt Generation
✅ PASS: Imagen API Parameters

4/4 tests passed
============================================================
```

## Troubleshooting

**"No module named 'anthropic'"**
```bash
pip3 install anthropic --break-system-packages
```

**"CLAUDE_API_KEY environment variable not set"**
```bash
export CLAUDE_API_KEY="sk-ant-..."
```

**Rate limits**
The test makes real Claude API calls. If you hit rate limits, wait a minute and try again.
