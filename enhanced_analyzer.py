#!/usr/bin/env python3
"""
Enhanced Analyzer with AppsFlyer Integration
Combines Amplitude, GA4, and AppsFlyer data for comprehensive weekly reports
"""

import os
import sys
import asyncio
from datetime import datetime
from dotenv import load_dotenv
import logging

# Import existing components
from amplitude_analyzer import AmplitudeAnalyzer
from appsflyer_weekly_integration import AppsFlyerWeeklyAnalyzer

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedWeeklyAnalyzer:
    def __init__(self):
        self.amplitude_analyzer = AmplitudeAnalyzer()
        self.appsflyer_analyzer = AppsFlyerWeeklyAnalyzer()
        
        # Check if AppsFlyer is configured
        self.appsflyer_enabled = bool(
            os.getenv('APPSFLYER_USERNAME') and 
            os.getenv('APPSFLYER_PASSWORD')
        )
        
        if not self.appsflyer_enabled:
            logger.warning("⚠️ AppsFlyer not configured - install data will be skipped")
    
    def get_week_info(self):
        """Get current ISO week information"""
        now = datetime.now()
        iso_calendar = now.isocalendar()
        current_year = iso_calendar[0]
        current_week = iso_calendar[1]
        
        # For weekly reports, analyze the previous complete week
        if current_week == 1:
            prev_year = current_year - 1
            dec31 = datetime(prev_year, 12, 31)
            prev_week = dec31.isocalendar()[1]
        else:
            prev_year = current_year
            prev_week = current_week - 1
        
        return {
            'current_year': current_year,
            'current_week': current_week,
            'analysis_year': prev_year,
            'analysis_week': prev_week
        }
    
    async def generate_comprehensive_report(self, headless: bool = True):
        """Generate comprehensive weekly report with all data sources"""
        
        week_info = self.get_week_info()
        
        logger.info("🚀 Generating Comprehensive Weekly Report")
        logger.info(f"   Analysis Week: {week_info['analysis_week']} of {week_info['analysis_year']}")
        
        # Initialize report sections
        report_sections = []
        
        # 1. Amplitude Analysis (existing functionality)
        logger.info("📊 Running Amplitude analysis...")
        try:
            if self.amplitude_analyzer.use_unified:
                # Use unified analyzer if GA4 is enabled
                unified_results = self.amplitude_analyzer.unified_analyzer.analyze_week_with_comparison()
                amplitude_section = unified_results.get('formatted_summary', 'Amplitude analysis failed')
            else:
                # Standard Amplitude analysis
                amplitude_results = self.amplitude_analyzer.analyze_week()
                amplitude_section = self.format_amplitude_results(amplitude_results)
            
            report_sections.append(amplitude_section)
            logger.info("✓ Amplitude analysis complete")
            
        except Exception as e:
            logger.error(f"❌ Amplitude analysis failed: {str(e)}")
            report_sections.append(f"❌ **Amplitude Analysis Error:** {str(e)}")
        
        # 2. AppsFlyer Analysis (new functionality)
        if self.appsflyer_enabled:
            logger.info("📱 Running AppsFlyer analysis...")
            try:
                appsflyer_summary = await self.appsflyer_analyzer.generate_weekly_appsflyer_summary(
                    week_info=week_info,
                    headless=headless
                )
                appsflyer_section = self.appsflyer_analyzer.format_appsflyer_insights(appsflyer_summary)
                report_sections.append(appsflyer_section)
                logger.info("✓ AppsFlyer analysis complete")
                
            except Exception as e:
                logger.error(f"❌ AppsFlyer analysis failed: {str(e)}")
                report_sections.append(f"❌ **AppsFlyer Analysis Error:** {str(e)}")
        
        # 3. Combined Executive Summary
        logger.info("📝 Generating executive summary...")
        executive_summary = self.generate_executive_summary(week_info, report_sections)
        
        # 4. Compile full report
        full_report = f"""# Weekly Analytics Report - Week {week_info['analysis_week']}, {week_info['analysis_year']}

{executive_summary}

{chr(10).join(report_sections)}

---
*Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
*Analysis period: Week {week_info['analysis_week']} of {week_info['analysis_year']}*
"""
        
        return full_report
    
    def format_amplitude_results(self, results):
        """Format Amplitude results into report section"""
        if not results:
            return "❌ No Amplitude data available"
        
        # This would format standard Amplitude results
        # For now, return a placeholder - you'd implement based on your existing format
        return "## 📈 Amplitude Session Analysis\n*Standard Amplitude analysis would go here*"
    
    def generate_executive_summary(self, week_info, report_sections):
        """Generate executive summary combining all data sources"""
        
        summary_lines = []
        summary_lines.append("## 🎯 Executive Summary")
        summary_lines.append(f"**Week {week_info['analysis_week']}, {week_info['analysis_year']} Performance Overview**")
        
        # Extract key metrics from report sections for summary
        # This is a simplified version - you'd parse the actual data
        
        summary_lines.append("")
        summary_lines.append("### Key Highlights")
        
        # Check for AppsFlyer data
        appsflyer_section = next((section for section in report_sections if "AppsFlyer" in section), None)
        if appsflyer_section:
            # Extract total installs from AppsFlyer section
            if "Total Installs:" in appsflyer_section:
                install_line = next((line for line in appsflyer_section.split('\n') if "Total Installs:" in line), None)
                if install_line:
                    summary_lines.append(f"- **Install Performance:** {install_line.split('**Total Installs:**')[1].strip()}")
        
        # Check for Amplitude data
        amplitude_section = next((section for section in report_sections if "Amplitude" in section), None)
        if amplitude_section and "Error" not in amplitude_section:
            summary_lines.append("- **Session Analysis:** Week-over-week analysis complete")
        
        summary_lines.append("")
        summary_lines.append("### Data Sources")
        summary_lines.append("- ✅ **Amplitude:** Session and conversion data")
        
        if self.appsflyer_enabled:
            summary_lines.append("- ✅ **AppsFlyer:** Install attribution and media source performance")
        else:
            summary_lines.append("- ⚠️ **AppsFlyer:** Not configured")
        
        if self.amplitude_analyzer.use_unified:
            summary_lines.append("- ✅ **GA4:** Comparative web analytics")
        else:
            summary_lines.append("- ⚠️ **GA4:** Not enabled")
        
        return "\n".join(summary_lines)
    
    async def run_weekly_report(self, headless: bool = True, send_slack: bool = True):
        """Run the complete weekly report workflow"""
        
        logger.info("🚀 Starting Enhanced Weekly Report")
        
        try:
            # Generate comprehensive report
            report = await self.generate_comprehensive_report(headless=headless)
            
            # Save to file
            week_info = self.get_week_info()
            filename = f"weekly_report_w{week_info['analysis_week']:02d}_{week_info['analysis_year']}.md"
            
            with open(filename, 'w') as f:
                f.write(report)
            
            logger.info(f"✅ Report saved: {filename}")
            
            # Send to Slack if configured and requested
            if send_slack and self.amplitude_analyzer.slack_webhook_url:
                try:
                    self.amplitude_analyzer.send_to_slack(report)
                    logger.info("✅ Report sent to Slack")
                except Exception as e:
                    logger.error(f"❌ Slack send failed: {str(e)}")
            
            # Print report to console
            print("\n" + "="*80)
            print("WEEKLY ANALYTICS REPORT")
            print("="*80)
            print(report)
            print("="*80)
            
            return report
            
        except Exception as e:
            logger.error(f"❌ Report generation failed: {str(e)}")
            return None

async def main():
    """Main execution function"""
    
    # Parse command line arguments
    headless = '--headless' in sys.argv or os.getenv('HEADLESS', 'true').lower() == 'true'
    no_slack = '--no-slack' in sys.argv
    
    analyzer = EnhancedWeeklyAnalyzer()
    
    try:
        report = await analyzer.run_weekly_report(
            headless=headless,
            send_slack=not no_slack
        )
        
        if report:
            logger.info("🎉 Enhanced weekly report completed successfully!")
        else:
            logger.error("❌ Report generation failed")
            sys.exit(1)
        
    except KeyboardInterrupt:
        logger.info("Report generation interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())