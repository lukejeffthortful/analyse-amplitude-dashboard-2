# GA4 Integration Plan for Amplitude Dashboard Analyzer

## Overview
This plan outlines the integration of Google Analytics 4 (GA4) session and purchase data into the existing Amplitude dashboard analyzer to provide a comprehensive cross-platform analytics view.

## Current State Analysis
- **Existing System**: Amplitude-based analyzer with dynamic week detection
- **Current Metrics**: Sessions, session conversion %, sessions per user, user conversion % (by Web/App platforms)
- **Output Formats**: Slack reports, JSON analysis, text summaries, Google Sheets format

## Integration Goals
1. **Session Comparison**: Record both Amplitude and GA4 session counts to contrast measurement differences
2. **Purchase Data**: Add GA4 e-commerce conversion and revenue metrics (GA4 exclusive)
3. **Measurement Analysis**: Identify and analyze variances between Amplitude vs GA4 session tracking
4. **Unified Reporting**: Maintain existing report formats with comparative GA4 insights

## Technical Architecture

### 1. Data Structure Design

```python
# Enhanced metrics structure
{
    'week_info': {
        'iso_week': 30,
        'year': 2025,
        'date_range': '2025-07-21 to 2025-07-27'
    },
    'amplitude_metrics': {
        'sessions': {...},
        'session_conversion': {...},
        'sessions_per_user': {...},
        'user_conversion': {...}
    },
    'ga4_metrics': {
        'sessions': {
            'total': {'current': 180000, 'previous': 165000, 'yoy_change': 9.1},
            'web': {'current': 120000, 'previous': 110000, 'yoy_change': 9.1},
            'mobile': {'current': 60000, 'previous': 55000, 'yoy_change': 9.1}
        },
        'conversions': {
            'purchase_events': {'current': 2500, 'previous': 2300, 'yoy_change': 8.7},
            'revenue': {'current': 85000, 'previous': 78000, 'yoy_change': 9.0}
        },
        'conversion_rate': {
            'total': {'current': 0.0139, 'previous': 0.0139, 'yoy_change': 0.0}
        }
    },
    'session_comparison': {
        'variance_analysis': {
            'total_sessions': {
                'amplitude': 203269,
                'ga4': 185420,
                'variance_pct': -8.8,  # (GA4 - Amplitude) / Amplitude * 100
                'variance_direction': 'ga4_lower'
            },
            'web_sessions': {
                'amplitude': 149215,
                'ga4': 134800,
                'variance_pct': -9.7
            },
            'app_sessions': {
                'amplitude': 54054,
                'ga4': 50620,
                'variance_pct': -6.4
            }
        },
        'tracking_insights': {
            'measurement_methodology': 'Amplitude uses events, GA4 uses pageviews/screenviews',
            'typical_variance_range': '5-15%',
            'variance_trend': 'ga4_consistently_lower'
        }
    }
}
```

### 2. Separated Data Handling Architecture

```python
# Separate data handlers for each platform
class AmplitudeDataHandler:
    """Handles Amplitude-specific data extraction and processing"""
    def get_weekly_yoy_data(self, target_week, target_year):
        # Current year data
        current_data = self.extract_platform_metrics(
            self.get_chart_data(), year=target_year, target_week=target_week
        )
        # Previous year data  
        previous_data = self.extract_platform_metrics(
            self.get_chart_data_previous(), year=target_year-1, target_week=target_week
        )
        return self.standardize_output(current_data, previous_data)

class GA4DataHandler:
    """Handles GA4-specific data extraction and processing"""
    def get_weekly_yoy_data(self, target_week, target_year):
        # GA4 uses different date range approach
        current_date_range = self.iso_week_to_ga4_dates(target_year, target_week)
        previous_date_range = self.iso_week_to_ga4_dates(target_year-1, target_week)
        
        current_data = self.query_ga4_sessions(current_date_range)
        previous_data = self.query_ga4_sessions(previous_date_range)
        
        return self.standardize_output(current_data, previous_data)

# Unified analyzer that combines standardized outputs
class UnifiedAnalyzer:
    def __init__(self):
        self.amplitude_handler = AmplitudeDataHandler()
        self.ga4_handler = GA4DataHandler()
    
    def analyze_weekly_data(self, target_week=None, target_year=None):
        # Get standardized data from both sources
        amplitude_metrics = self.amplitude_handler.get_weekly_yoy_data(target_week, target_year)
        ga4_metrics = self.ga4_handler.get_weekly_yoy_data(target_week, target_year)
        
        # Compare using identical data structures
        return self.compare_standardized_metrics(amplitude_metrics, ga4_metrics)
```

### 3. Standardized Output Format

Both handlers output identical data structures for easy comparison:

```python
# Standardized format from both AmplitudeDataHandler and GA4DataHandler
standardized_metrics = {
    'sessions': {
        'apps': {
            'current': 54054,
            'previous': 40656, 
            'yoy_change': 33.0
        },
        'web': {
            'current': 149215,
            'previous': 174835,
            'yoy_change': -14.7
        },
        'combined': {
            'current': 203269,
            'previous': 215491,
            'yoy_change': -5.7
        }
    },
    # GA4 includes additional e-commerce metrics
    'conversions': {  # GA4 only
        'purchase_events': {
            'current': 2500,
            'previous': 2300,
            'yoy_change': 8.7
        },
        'revenue': {
            'current': 85000,
            'previous': 78000,
            'yoy_change': 9.0
        }
    },
    'metadata': {
        'source': 'amplitude' | 'ga4',
        'iso_week': 30,
        'year': 2025,
        'date_range': '2025-07-21 to 2025-07-27'
    }
}
```

### 4. GA4-Specific Date Handling

```python
class GA4DataHandler:
    def iso_week_to_ga4_dates(self, year, week):
        """Convert ISO week to GA4 date range format"""
        monday, sunday = self.get_week_date_range(year, week)
        return {
            'start_date': monday.strftime('%Y-%m-%d'),
            'end_date': sunday.strftime('%Y-%m-%d')
        }
    
    def query_ga4_sessions(self, date_range):
        """GA4-specific session query with platform breakdown"""
        request = RunReportRequest(
            property=f"properties/{self.property_id}",
            dimensions=[
                Dimension(name="platformDeviceCategory")  # web, mobile, tablet
            ],
            metrics=[
                Metric(name="sessions"),
                Metric(name="conversions"),
                Metric(name="purchaseRevenue")
            ],
            date_ranges=[DateRange(
                start_date=date_range['start_date'], 
                end_date=date_range['end_date']
            )]
        )
        return self.client.run_report(request)
```

## Implementation Plan

### Phase 1: GA4 Client Setup (Week 1)
**Tasks:**
1. **Environment Setup**
   - Install `google-analytics-data` package
   - Create GA4 service account and credentials
   - Add GA4 property ID to environment variables

2. **GA4DataHandler Class**
   - Implement authentication with service account
   - Create GA4-specific date handling (ISO week → GA4 date ranges)
   - Add quota monitoring and rate limiting
   - Build standardized output methods

3. **AmplitudeDataHandler Refactor**
   - Extract existing Amplitude logic into separate handler
   - Maintain current functionality while standardizing output
   - Ensure backward compatibility

4. **Configuration**
   - Add GA4_PROPERTY_ID to .env
   - Create GA4_SERVICE_ACCOUNT_PATH config
   - Update .env.example with new variables

**Deliverables:**
- `ga4_data_handler.py` - GA4-specific data handling
- `amplitude_data_handler.py` - Refactored Amplitude handler  
- Updated environment configuration
- Basic connection testing script

### Phase 2: Data Extraction (Week 1-2)
**Tasks:**
1. **GA4 Data Extraction**
   - Implement GA4 session queries with platformDeviceCategory breakdown
   - Handle GA4-specific date range format (YYYY-MM-DD)
   - Extract purchase events and revenue data
   - Build YoY comparison logic (same ISO week, different years)

2. **Amplitude Data Standardization**
   - Refactor existing extraction to use standardized output format
   - Maintain current CSV parsing logic
   - Ensure ISO week handling consistency

3. **Output Standardization**
   - Both handlers produce identical data structure
   - Include metadata (source, date_range, iso_week)
   - Handle missing data gracefully

**Deliverables:**
- GA4 session/conversion extraction methods
- Standardized Amplitude data handler
- Unified output format implementation

### Phase 3: Data Integration (Week 2)
**Tasks:**
1. **UnifiedAnalyzer Implementation**
   - Create analyzer that combines both standardized data sources
   - Implement variance calculation between identical data structures
   - Add comparative analysis methods

2. **Backward Compatibility**
   - Maintain existing AmplitudeAnalyzer functionality
   - Add GA4 toggle without breaking current workflows
   - Ensure existing reports work unchanged when GA4 disabled

3. **Error Handling & Fallbacks**
   - Handle GA4 API failures gracefully (quota, network, auth)
   - Automatic fallback to Amplitude-only analysis
   - Clear error messaging and logging

**Deliverables:**
- UnifiedAnalyzer class with separated data handlers
- Variance analysis for standardized metrics
- Robust error handling with fallback modes

### Phase 4: Reporting Enhancement (Week 2-3)
**Tasks:**
1. **Slack Report Updates**
   - Add GA4 vs Amplitude session comparison sections
   - Include variance analysis with directional indicators
   - Show both measurement methodologies side-by-side

2. **Google Sheets Format**
   - Add GA4 session counts alongside Amplitude sessions
   - Include variance percentages in summary
   - Add separate section comparing measurement approaches

3. **JSON/Text Outputs**
   - Add comparative session analysis to existing outputs
   - Include variance trends and insights
   - Maintain data structure consistency

**Deliverables:**
- Updated Slack reporting with session comparisons
- Enhanced Google Sheets format with variance analysis
- Comprehensive JSON output with comparative metrics

### Example Comparative Report Output

```
Week 30 Analysis (2025-07-21 to 2025-07-27):

📊 SESSION COMPARISON
Amplitude Sessions: 203,269 vs 215,491 (down 5.7% YoY)
GA4 Sessions: 185,420 vs 198,350 (down 6.5% YoY)
Variance: GA4 shows 8.8% fewer sessions than Amplitude

Platform Analysis:
Web Sessions: 
  • Amplitude: 149,215 vs 174,835 (down 14.7% YoY)
  • GA4: 134,800 vs 158,200 (down 14.8% YoY)
  • Variance: GA4 tracks 9.7% fewer web sessions

App Sessions:
  • Amplitude: 54,054 vs 40,656 (up 33.0% YoY) 
  • GA4: 50,620 vs 40,150 (up 26.1% YoY)
  • Variance: GA4 tracks 6.4% fewer app sessions

💰 GA4 E-COMMERCE METRICS
Purchase Events: 2,500 vs 2,300 (up 8.7% YoY)
Revenue: £85,000 vs £78,000 (up 9.0% YoY)
GA4 Conversion Rate: 1.35% vs 1.16% (up 0.19 ppts YoY)

🔍 MEASUREMENT INSIGHTS
• GA4 consistently shows 6-10% fewer sessions than Amplitude
• YoY growth trends are similar between both platforms
• Web variance higher than app variance (tracking methodology differences)
```

### Phase 5: Advanced Analytics (Week 3)
**Tasks:**
1. **Session Measurement Analysis**
   - Analyze GA4 vs Amplitude session variance patterns over time
   - Identify consistent measurement differences
   - Document methodology differences and their impact

2. **Attribution Insights**
   - Compare traffic source attribution
   - Analyze conversion funnel differences
   - Add platform-specific insights

3. **Historical Variance Trends**
   - Track session variance patterns over time
   - Alert on significant measurement drift
   - Provide insights on tracking consistency

**Deliverables:**
- Session variance analysis features
- Measurement methodology documentation
- Trend analysis for session tracking differences

## Configuration Requirements

### Environment Variables
```bash
# Existing Amplitude config
AMPLITUDE_API_KEY=your_amplitude_key
AMPLITUDE_SECRET_KEY=your_amplitude_secret
SLACK_WEBHOOK_URL=your_slack_webhook

# New GA4 config
GA4_PROPERTY_ID=123456789
GA4_SERVICE_ACCOUNT_PATH=/path/to/service-account.json
GA4_ENABLED=true  # Toggle GA4 integration
```

### GA4 Setup Requirements
1. **Google Cloud Project**
   - Enable GA4 Reporting API
   - Create service account with Analytics Viewer role
   - Download service account JSON key

2. **GA4 Property Access**
   - Add service account email as Viewer to GA4 property
   - Verify data availability for target date ranges
   - Test API access with basic queries

## Data Mapping Strategy

### Session Comparison Framework
| Metric | Amplitude | GA4 | Comparison Purpose |
|--------|-----------|-----|-------------------|
| Total Sessions | 203,269 | 185,420 | Identify measurement variance (-8.8%) |
| Web Sessions | 149,215 | 134,800 | Platform-specific tracking differences |
| App Sessions | 54,054 | 50,620 | Mobile measurement comparison |
| YoY Session Change | -5.7% | -12.3% | Growth measurement consistency |

### GA4-Exclusive Metrics (No Amplitude Equivalent)
| GA4 Metric | Purpose | Notes |
|------------|---------|-------|
| Purchase Events | E-commerce conversion tracking | GA4 specific functionality |
| Revenue | Financial performance | GA4 e-commerce data |
| Conversion Rate (GA4) | GA4-based conversion analysis | Different from Amplitude conversion |

### Platform Mapping
| Amplitude Platform | GA4 Dimension | Filter/Segment |
|-------------------|---------------|----------------|
| Web | `sessionSourceMedium` | `platformDeviceCategory == 'desktop'` |
| App | `sessionSourceMedium` | `platformDeviceCategory == 'mobile'` |
| Combined | All sessions | No filter |

## Risk Assessment & Mitigation

### Technical Risks
1. **API Rate Limits**
   - **Risk**: GA4 API quota exhaustion
   - **Mitigation**: Implement exponential backoff, cache results, optimize queries

2. **Data Variance**
   - **Risk**: Significant differences between Amplitude and GA4
   - **Mitigation**: Clear documentation of differences, variance alerts

3. **Authentication Issues**
   - **Risk**: Service account access problems
   - **Mitigation**: Comprehensive error handling, fallback to Amplitude-only

### Business Risks
1. **Session Metric Confusion**
   - **Risk**: Users confused by different session counts from two sources
   - **Mitigation**: Clear labeling showing "Amplitude Sessions" vs "GA4 Sessions", documentation explaining differences

2. **Variance Interpretation**
   - **Risk**: Misunderstanding why GA4 and Amplitude show different numbers
   - **Mitigation**: Educational content on measurement methodologies, clear variance explanations

## Success Metrics
1. **Technical Success**
   - 99%+ API success rate
   - <30 second report generation time
   - <15% data variance between platforms

2. **Business Success**
   - Enhanced insight depth in weekly reports
   - Improved tracking coverage visibility
   - Actionable cross-platform recommendations

## Timeline Summary
- **Week 1**: GA4 setup, basic data extraction
- **Week 2**: Data integration, enhanced reporting
- **Week 3**: Advanced analytics, production deployment

## Next Steps
1. **Review and Approval**: Get stakeholder sign-off on plan
2. **Environment Setup**: Prepare GA4 credentials and access
3. **Development Start**: Begin Phase 1 implementation

---

**Questions for Review:**
1. Does the separated data handler architecture (AmplitudeDataHandler vs GA4DataHandler) make sense?
2. Are the standardized output formats appropriate for easy comparison?
3. Is the GA4 platformDeviceCategory mapping to web/app sufficient?
4. Should we include additional GA4 e-commerce metrics (add_to_cart, begin_checkout)?
5. Is the 3-week timeline realistic for this separated architecture approach?
6. Any specific requirements for how variance analysis should be presented?