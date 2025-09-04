#!/usr/bin/env python3
"""
Check week 35 dates for 2024 and 2025
"""

from datetime import datetime
from appsflyer_weekly_integration import AppsFlyerWeeklyAnalyzer

analyzer = AppsFlyerWeeklyAnalyzer()

# Check week 35 for both years
for year in [2024, 2025]:
    monday, sunday = analyzer.get_iso_week_dates(year, 35)
    print(f"\nWeek 35 of {year}:")
    print(f"  Monday: {monday.strftime('%Y-%m-%d (%A)')}")
    print(f"  Sunday: {sunday.strftime('%Y-%m-%d (%A)')}")
    
# Also check what your reference file dates are
print(f"\nYour reference file is for: 2024-08-25 to 2024-08-31")
ref_start = datetime(2024, 8, 25)
ref_end = datetime(2024, 8, 31)
print(f"  Start: {ref_start.strftime('%Y-%m-%d (%A)')}")
print(f"  End: {ref_end.strftime('%Y-%m-%d (%A)')}")

# What week is that?
week_num = ref_start.isocalendar()[1]
print(f"  This is ISO week: {week_num}")

# For 2025
print(f"\nFor 2025, Aug 25-31:")
start_2025 = datetime(2025, 8, 25)
end_2025 = datetime(2025, 8, 31) 
print(f"  Start: {start_2025.strftime('%Y-%m-%d (%A)')}")
print(f"  End: {end_2025.strftime('%Y-%m-%d (%A)')}")
week_2025 = start_2025.isocalendar()[1]
print(f"  This is ISO week: {week_2025}")