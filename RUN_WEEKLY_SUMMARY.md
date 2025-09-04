# How to Run Full Weekly Summary with GA4 Acquisition

## Prerequisites

1. **Install Dependencies:**
```bash
pip install -r requirements.txt
```

2. **Install Playwright (for AppsFlyer automation):**
```bash
pip install playwright
playwright install chromium
```

## Running Options

### Option 1: Enhanced Weekly Analyzer (Recommended)
**Complete analysis with all platforms + GA4 acquisition reconciliation:**

```bash
python3 enhanced_weekly_analyzer.py
```

**What this provides:**
- 🎯 Executive Summary with key metrics and insights
- 📈 Amplitude Session Analysis (YoY)
- 📱 AppsFlyer Install Attribution (YoY, unified SKAN+Traditional)
- 🔄 Acquisition Platform Reconciliation (AppsFlyer vs GA4)
- 📊 GA4 User Acquisition Details (channels, sources)

### Option 2: Individual Components
**Run components separately:**

```bash
# 1. Amplitude sessions
python3 amplitude_analyzer.py

# 2. AppsFlyer installs with YoY
python3 appsflyer_weekly_integration.py

# 3. GA4 acquisition data
python3 ga4_acquisition_handler.py

# 4. Acquisition reconciliation
python3 acquisition_reconciliation.py
```

### Option 3: Test with Mock Data (No Dependencies)
**If you want to see the structure without full execution:**

```bash
# Show GA4 breakdown format
python3 show_ga4_breakdown.py

# Verify unified dashboard data
python3 verify_unified_data.py
```

## Expected Output Structure

The enhanced weekly analyzer will generate a report like this:

```
# 📊 Comprehensive Weekly Report - Week 35, 2025
**Period:** 2025-08-25 to 2025-08-31

## 🎯 Executive Summary
- **Sessions:** [Amplitude data] ([YoY change]%)
- **App Installs:** 3,125 (-22.5% YoY)
- **GA4 New Users:** [GA4 total]

### Key Insights
- GA4 tracking [difference]% fewer new users than AppsFlyer
- [Cross-platform insights]

### Recommended Actions
- [Specific recommendations based on reconciliation]

## 📈 Amplitude Session Analysis
[Session metrics with YoY comparisons]

## 📱 AppsFlyer Install Attribution
**Total Installs:** 3,125 (-22.5% YoY vs 2024: 4,033)

**Top Media Sources (2025):**
- organic: 1,726 (55.2%)
- googleadwords_int: 638 (20.4%)
- website-thortful: 506 (16.2%)
- google_organic_seo: 175 (5.6%)
- bloomreach: 50 (1.6%)

## 🔄 Acquisition Platform Reconciliation
**Summary:**
- **AppsFlyer Installs:** 3,125
- **GA4 New Users:** [GA4 total]
- **Difference:** [difference] ([percent]%)

**Channel Comparison:**
| Channel | AppsFlyer | GA4 | Difference | % Diff |
|---------|-----------|-----|------------|--------|
| Paid Search | 638 | [GA4] | [diff] | [%] |
| Direct | 1,726 | [GA4] | [diff] | [%] |
| Referral | 506 | [GA4] | [diff] | [%] |

## 📊 GA4 User Acquisition Details
**Total New Users:** [total]

**Top Acquisition Channels:**
- [Channel breakdown from GA4]

**Top Sources:**
- [Source breakdown from GA4]
```

## Current Status

✅ **Updated Components:**
- AppsFlyer unified dashboard (SKAN + Traditional attribution) 
- GA4 acquisition handler ready
- Acquisition reconciliation configured
- Enhanced weekly analyzer created

🔄 **Ready to Run:** Once dependencies are installed, run `python3 enhanced_weekly_analyzer.py`