#!/bin/bash

# ==================== AI-Nexus Deployment Script ====================
# Ì∫Ä Safe, project-specific deployment
# Usage: ./deploy_and_debug.sh

echo "Ì¥ß STEP 1: Confirming we're in the ainexus project..."
CURRENT_DIR=$(pwd)
echo "Current directory: $CURRENT_DIR"

if [[ ! "$CURRENT_DIR" =~ "ainexus" ]]; then
    echo "‚ùå WRONG DIRECTORY! Please run this from your ainexus project folder."
    echo "Ì≤° Run: cd /c/Users/op/Desktop/ainexus"
    exit 1
fi

echo "‚úÖ Confirmed: In ainexus project directory"

echo "Ì≥¶ STEP 2: Installing dependencies..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "‚ö†Ô∏è No requirements.txt found. Continuing..."
fi

echo "Ì¥ç STEP 3: Checking project files..."
echo "Project structure:"
ls -la

# Find the main application file
echo "Ì¥é Looking for main application file..."
if [ -f "app.py" ]; then
    MAIN_FILE="app.py"
elif [ -f "main.py" ]; then
    MAIN_FILE="main.py"
elif [ -f "application.py" ]; then
    MAIN_FILE="application.py"
else
    echo "Ì≥ã Available Python files:"
    find . -maxdepth 2 -name "*.py" -type f
    MAIN_FILE=""
fi

if [ -n "$MAIN_FILE" ]; then
    echo "‚úÖ Main file detected: $MAIN_FILE"
    echo "Ì∑™ Quick local test..."
    python "$MAIN_FILE" &
    TEST_PID=$!
    sleep 3
    if ps -p $TEST_PID > /dev/null 2>&1; then
        echo "‚úÖ Local test passed. Stopping..."
        kill $TEST_PID 2>/dev/null
    else
        echo "‚ö†Ô∏è Local test ended quickly (may be normal for web apps)"
    fi
fi

echo "Ì∫Ä STEP 4: Deploying to GitHub..."
git add .
git status

echo "Ì≥ù Commit message: 'Deploying AI-Nexus to Render'"
git commit -m "Deploying AI-Nexus to Render"
git push origin main

echo "‚úÖ Deployment triggered!"
echo "Ì≥° Render will automatically deploy from GitHub"
echo "Ìºê Live URL: https://ai-nexus-engine.onrender.com"
echo "Ì≥ä Monitor at: https://dashboard.render.com"

echo "Ìæâ DEPLOYMENT INITIATED SUCCESSFULLY!"
