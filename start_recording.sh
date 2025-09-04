#!/bin/bash
# Start Playwright recording session

echo "Starting Playwright Codegen..."
echo "This will open:"
echo "1. A browser window - perform your export workflow here"
echo "2. Playwright Inspector - shows generated code in real-time"
echo ""
echo "When done, copy the code from Playwright Inspector"
echo ""

source venv/bin/activate
playwright codegen https://hq1.appsflyer.com/auth/login --save-storage=auth.json

echo ""
echo "Recording complete!"
echo "Auth state saved to: auth.json"