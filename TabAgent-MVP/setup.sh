#!/bin/bash
# Tab Agent MVP - Setup Script

set -e

echo "============================================================"
echo "Tab Agent MVP - Automated Setup"
echo "============================================================"
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python --version 2>&1 | grep -oP '\d+\.\d+')
python_major=$(echo $python_version | cut -d. -f1)
python_minor=$(echo $python_version | cut -d. -f2)

if [ "$python_major" -lt 3 ] || { [ "$python_major" -eq 3 ] && [ "$python_minor" -lt 8 ]; }; then
    echo "❌ Python 3.8+ required. You have: $python_version"
    exit 1
fi

echo "✅ Python $python_version detected"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
if [ -d "env" ]; then
    echo "⚠️  env/ already exists. Skipping..."
else
    python -m venv env
    echo "✅ Virtual environment created"
fi
echo ""

# Activate
echo "Activating virtual environment..."
source env/bin/activate

# Install dependencies
echo "Installing dependencies..."
echo "(This may take 2-3 minutes)"
echo ""

pip install --upgrade pip -q
pip install -r requirements.txt

echo ""
echo "✅ Dependencies installed"
echo ""

# Test installation
echo "Testing installation..."
python test_pipeline.py

echo ""
echo "============================================================"
echo "✅ SETUP COMPLETE"
echo "============================================================"
echo ""
echo "Next steps:"
echo "  1. Activate environment: source env/bin/activate"
echo "  2. Add audio to input/"
echo "  3. Run: python main.py your_song.wav"
echo ""
echo "See QUICKSTART.md for more details"
echo ""
