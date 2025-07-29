#!/usr/bin/env python3
"""
Test script to show Google Sheets formatted output
"""
import json
from amplitude_analyzer import AmplitudeAnalyzer

# Load the latest analysis data
with open('weekly_analysis.json', 'r') as f:
    analysis_data = json.load(f)

analyzer = AmplitudeAnalyzer()
sheets_data = analyzer.format_for_google_sheets(analysis_data)

print("Google Sheets formatted data (tab-separated):")
print("=" * 80)
print(sheets_data)
print("=" * 80)
print("\nThis data can be copied and pasted directly into Google Sheets.")
print("The tabs will automatically create separate columns.")