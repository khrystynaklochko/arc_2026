#!/bin/bash
# Quick Start Script for Kaggle Submission
# ARC Prize 2026 - ARC-AGI-3

set -e

echo "=================================================="
echo "ARC Prize 2026 - Kaggle Submission Quick Start"
echo "=================================================="

# Check Python version
echo ""
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
required_version="3.12"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Error: Python 3.12+ required (found $python_version)"
    echo "Please upgrade Python: https://www.python.org/downloads/"
    exit 1
fi

echo "✅ Python $python_version"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo "✅ Dependencies installed"

# Check .env file
if [ ! -f ".env" ]; then
    echo ""
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your API keys"
fi

# Create output directories
mkdir -p submissions
mkdir -p evaluations

echo ""
echo "=================================================="
echo "Setup Complete! 🎉"
echo "=================================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Edit .env file with your API keys:"
echo "   nano .env"
echo ""
echo "2. Test with a single game:"
echo "   python play.py"
echo ""
echo "3. Run baseline evaluation:"
echo "   python batch_evaluator.py --agent random"
echo ""
echo "4. Generate Kaggle submission:"
echo "   python kaggle_submission.py --agent random"
echo ""
echo "5. Validate submission:"
echo "   python kaggle_submission.py --validate-only submissions/submission_*.json"
echo ""
echo "6. Upload to Kaggle:"
echo "   https://www.kaggle.com/competitions/arc-prize-2026-arc-agi-3"
echo ""
echo "For more information, see KAGGLE.md"
echo "=================================================="

# Made with Bob
