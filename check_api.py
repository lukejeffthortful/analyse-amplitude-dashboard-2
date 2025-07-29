#!/usr/bin/env python3
"""
Simple script to check if Amplitude API is available
"""

import requests
from dotenv import load_dotenv
import os

load_dotenv()

def check_api_status():
    api_key = os.getenv('AMPLITUDE_API_KEY')
    secret_key = os.getenv('AMPLITUDE_SECRET_KEY')
    
    # Try the lightest chart (Sessions - cost 1120)
    url = "https://amplitude.com/api/3/chart/y0ivh3am/csv"
    
    try:
        response = requests.get(url, auth=(api_key, secret_key), timeout=10)
        print(f"API Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ API Available - Ready to run real data analysis!")
            return True
        elif response.status_code == 429:
            error_data = response.json()
            print(f"⏱️  Rate Limited: {error_data.get('error', {}).get('metadata', {}).get('details', 'Unknown error')}")
            print("Wait a few minutes and try again.")
            return False
        else:
            print(f"❌ API Error: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return False

if __name__ == "__main__":
    print("🔍 Checking Amplitude API status...")
    check_api_status()