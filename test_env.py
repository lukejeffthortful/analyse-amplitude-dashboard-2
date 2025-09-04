#!/usr/bin/env python3
"""Quick test to check environment variables"""

import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

print("Environment Variables Check:")
print("-" * 40)

# Check all relevant variables
vars_to_check = [
    'AMPLITUDE_API_KEY',
    'AMPLITUDE_SECRET_KEY',
    'APPSFLYER_API_TOKEN',
    'APPSFLYER_APP_ID',
    'GA4_ENABLED',
    'SLACK_WEBHOOK_URL'
]

for var in vars_to_check:
    value = os.getenv(var)
    if value:
        # Mask sensitive values
        if 'KEY' in var or 'TOKEN' in var or 'SECRET' in var:
            masked = value[:4] + '...' + value[-4:] if len(value) > 8 else '***'
            print(f"{var}: {masked}")
        else:
            print(f"{var}: {value}")
    else:
        print(f"{var}: NOT SET")

print("\n.env file location:", os.path.abspath('.env'))
print("Current directory:", os.getcwd())