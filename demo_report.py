#!/usr/bin/env python3
"""
Demo script to show how the Amplitude report would look and send it to Slack
"""

import os
import requests
from dotenv import load_dotenv
from amplitude_analyzer import AmplitudeAnalyzer

load_dotenv()

def create_sample_analysis():
    """Create a sample analysis with realistic data based on the expected format."""
    return {
        'week_info': {
            'iso_week': 29,
            'year': 2025,
            'date_range': '2025-07-14 to 2025-07-20'
        },
        'metrics': {
            'sessions': {
                'apps': {'current': 4074.0, 'previous': 41014.0, 'yoy_change': -90.1},
                'web': {'current': 12808.0, 'previous': 174835.0, 'yoy_change': -92.7},
                'combined': {'current': 16882.0, 'previous': 215849.0, 'yoy_change': -92.2}
            },
            'sessions_per_user': {
                'apps': {'current': 1.15, 'previous': 1.28, 'yoy_change': -10.2},
                'web': {'current': 1.16, 'previous': 1.39, 'yoy_change': -16.5},
                'combined': {'current': 1.23, 'previous': 1.46, 'yoy_change': -15.8}
            },
            'session_conversion': {
                'apps': {'current': 0.218, 'previous': 0.228, 'yoy_change': -1.0},
                'web': {'current': 0.201, 'previous': 0.171, 'yoy_change': 3.0},
                'combined': {'current': 0.206, 'previous': 0.188, 'yoy_change': 1.8}
            },
            'user_conversion': {
                'apps': {'current': 0.218, 'previous': 0.203, 'yoy_change': 1.5},
                'web': {'current': 0.201, 'previous': 0.186, 'yoy_change': 1.5},
                'combined': {'current': 0.206, 'previous': 0.191, 'yoy_change': 1.5}
            }
        }
    }

def generate_sample_summary(analysis_data):
    """Use the actual AmplitudeAnalyzer to generate the enhanced summary."""
    analyzer = AmplitudeAnalyzer()
    return analyzer.generate_executive_summary(analysis_data)

def main():
    # Create sample data
    sample_analysis = create_sample_analysis()
    sample_summary = generate_sample_summary(sample_analysis)
    
    print("📊 SAMPLE AMPLITUDE WEEKLY REPORT")
    print("=" * 50)
    print(sample_summary)
    print("=" * 50)
    
    # Create analyzer instance and send to Slack
    analyzer = AmplitudeAnalyzer()
    
    # Save sample files
    with open('sample_weekly_summary.txt', 'w') as f:
        f.write(sample_summary)
    
    import json
    with open('sample_weekly_analysis.json', 'w') as f:
        json.dump(sample_analysis, f, indent=2)
    
    print("\n📁 Sample files saved:")
    print("- sample_weekly_summary.txt")
    print("- sample_weekly_analysis.json")
    
    # Send to Slack
    print(f"\n📤 Sending report to Slack...")
    success = analyzer.send_to_slack(sample_summary, sample_analysis)
    
    if success:
        print("✅ Sample report sent to your Slack channel!")
    else:
        print("❌ Failed to send report to Slack")

if __name__ == "__main__":
    main()