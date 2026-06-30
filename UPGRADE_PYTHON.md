# Upgrade Python to 3.12+

## Current Status
- **Current Python**: 3.9.13
- **Required**: Python 3.12+
- **System**: macOS

## Upgrade Instructions

### Option 1: Using Homebrew (Recommended for macOS)

```bash
# Install Python 3.12
brew install python@3.12

# Verify installation
python3.12 --version

# Create alias (optional)
echo 'alias python3=python3.12' >> ~/.zshrc
source ~/.zshrc

# Or use python3.12 directly
python3.12 full_play_test.py
```

### Option 2: Using pyenv (For Multiple Python Versions)

```bash
# Install pyenv if not already installed
brew install pyenv

# Install Python 3.12
pyenv install 3.12.0

# Set as local version for this project
cd /Users/chris/Developer/arc
pyenv local 3.12.0

# Verify
python --version
```

### Option 3: Download from Python.org

1. Go to https://www.python.org/downloads/
2. Download Python 3.12+ for macOS
3. Run the installer
4. Verify: `python3.12 --version`

## After Upgrading

### 1. Create Virtual Environment

```bash
cd /Users/chris/Developer/arc

# Create venv with Python 3.12
python3.12 -m venv venv

# Activate
source venv/bin/activate

# Verify Python version
python --version  # Should show 3.12+
```

### 2. Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install requirements
pip install -r requirements.txt
```

### 3. Run Full Test

```bash
# Run the comprehensive test
python full_play_test.py
```

Expected output:
```
============================================================
  ARC-AGI-3 FULL PLAY TEST
  Testing all components
============================================================

[Tests will run...]

============================================================
  TEST SUMMARY
============================================================
✅ PASS | Basic Environment
✅ PASS | Random Agent
✅ PASS | Toolkit
✅ PASS | Environment Wrapper
✅ PASS | Batch Evaluator
✅ PASS | Kaggle Submission
✅ PASS | LLM Agents

------------------------------------------------------------
Results: 7/7 tests passed (100.0%)
------------------------------------------------------------

🎉 ALL TESTS PASSED!
```

### 4. Run Other Tests

```bash
# Test basic gameplay
python play.py

# Test agent
python run_agent.py

# Batch evaluation
python batch_evaluator.py --agent random

# Generate Kaggle submission
python kaggle_submission.py --agent random
```

## Quick Start Script

Alternatively, use the automated setup script:

```bash
# This will check Python version and guide you
./quick_start_kaggle.sh
```

## Troubleshooting

### Issue: Command not found

```bash
# If python3.12 not in PATH after brew install
brew link python@3.12

# Or use full path
/opt/homebrew/bin/python3.12 full_play_test.py
```

### Issue: Multiple Python versions

```bash
# Check all Python versions
ls -l /usr/local/bin/python*
ls -l /opt/homebrew/bin/python*

# Use specific version
/opt/homebrew/bin/python3.12 full_play_test.py
```

### Issue: Permission denied

```bash
# Make scripts executable
chmod +x full_play_test.py
chmod +x quick_start_kaggle.sh
```

## Verification Checklist

After upgrading, verify:

- [ ] Python version is 3.12+: `python --version`
- [ ] pip is working: `pip --version`
- [ ] Dependencies installed: `pip list | grep arc-agi`
- [ ] Test script runs: `python full_play_test.py`
- [ ] All tests pass: Check for "ALL TESTS PASSED"

## Next Steps After Successful Test

1. **Develop your agent**
   ```bash
   # Edit agents/llm_agent.py or create new agent
   ```

2. **Test locally**
   ```bash
   python batch_evaluator.py --agent myagent
   ```

3. **Generate submission**
   ```bash
   python kaggle_submission.py --agent myagent
   ```

4. **Upload to Kaggle**
   - Go to: https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3
   - Submit your `submissions/submission_*.json` file

## Support

If you encounter issues:
1. Check Python version: `python --version`
2. Check installation: `which python3.12`
3. Try with full path: `/opt/homebrew/bin/python3.12`
4. Reinstall: `brew reinstall python@3.12`