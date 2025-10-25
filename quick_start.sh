#!/bin/bash

# Quick Start Script for YouTube-to-Instagram Agent

set -e

echo "🤖 YouTube-to-Instagram Agent - Quick Start"
echo "=========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python3 --version

# Check if FFmpeg is installed
echo "Checking FFmpeg..."
if ! command -v ffmpeg &> /dev/null
then
    echo "❌ FFmpeg not found. Please install FFmpeg first:"
    echo "   Ubuntu/Debian: sudo apt install ffmpeg"
    echo "   macOS: brew install ffmpeg"
    exit 1
fi
echo "✅ FFmpeg found"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo ""
    echo "⚠️  Please edit .env file with your credentials:"
    echo "   - INSTAGRAM_USERNAME"
    echo "   - INSTAGRAM_PASSWORD"
    echo "   - OPENAI_API_KEY or ANTHROPIC_API_KEY"
    echo ""
    read -p "Press Enter after you've configured .env..."
fi

# Create necessary directories
mkdir -p data/videos data/edited logs

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Edit config.yaml to customize your settings"
echo "  2. Run in test mode: python main.py --test"
echo "  3. Make your first post: python main.py"
echo "  4. Run in daemon mode: python main.py --daemon"
echo ""
echo "For more information, see SETUP.md"
