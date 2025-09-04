#!/usr/bin/env python3
"""
Verify Unified Dashboard Data
Check that SKAN + Traditional attribution provides different/comprehensive data
"""

import csv
import logging
from pathlib import Path
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def analyze_csv_file(file_path: Path) -> dict:
    """Analyze AppsFlyer CSV file without pandas"""
    
    if not file_path.exists():
        return {'error': f"File not found: {file_path}"}
    
    data = {
        'total_installs': 0,
        'media_sources': defaultdict(int),
        'campaigns': defaultdict(int),
        'row_count': 0,
        'columns': []
    }
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data['columns'] = reader.fieldnames or []
            
            # Find the install column
            install_col = None
            for col in data['columns']:
                if 'install' in col.lower() and ('appsflyer' in col.lower() or 'af' in col.lower()):
                    install_col = col
                    break
            
            if not install_col:
                # Try common variations
                for col in data['columns']:
                    if col.lower() in ['installs', 'install', 'installs_appsflyer']:
                        install_col = col
                        break
            
            media_source_col = None
            for col in data['columns']:
                if 'media' in col.lower() and 'source' in col.lower():
                    media_source_col = col
                    break
            
            campaign_col = None
            for col in data['columns']:
                if 'campaign' in col.lower():
                    campaign_col = col
                    break
            
            logger.info(f"📊 Analyzing {file_path.name}")
            logger.info(f"   Install column: {install_col}")
            logger.info(f"   Media source column: {media_source_col}")
            logger.info(f"   Campaign column: {campaign_col}")
            
            for row in reader:
                data['row_count'] += 1
                
                # Count installs
                if install_col and row.get(install_col):
                    try:
                        installs = int(float(row[install_col]))
                        data['total_installs'] += installs
                        
                        # Group by media source
                        if media_source_col and row.get(media_source_col):
                            source = row[media_source_col]
                            data['media_sources'][source] += installs
                        
                        # Group by campaign
                        if campaign_col and row.get(campaign_col):
                            campaign = row[campaign_col]
                            data['campaigns'][campaign] += installs
                            
                    except (ValueError, TypeError):
                        continue
        
        # Sort by volume
        data['media_sources'] = dict(sorted(data['media_sources'].items(), key=lambda x: x[1], reverse=True))
        data['campaigns'] = dict(sorted(data['campaigns'].items(), key=lambda x: x[1], reverse=True))
        
        return data
        
    except Exception as e:
        return {'error': f"Failed to analyze {file_path}: {str(e)}"}

def compare_unified_data():
    """Compare data between years to verify different results"""
    
    logger.info("🔄 Verifying Unified Dashboard Data Differences")
    logger.info("="*60)
    
    # Find the week 35 files
    data_dir = Path("./appsflyer_data")
    
    file_2024 = data_dir / "2024" / "week_35_20240826_20240901.csv"
    file_2025 = data_dir / "2025" / "week_35_20250825_20250831.csv"
    
    if not file_2024.exists():
        logger.error(f"❌ 2024 file not found: {file_2024}")
        return
        
    if not file_2025.exists():
        logger.error(f"❌ 2025 file not found: {file_2025}")
        return
    
    # Analyze both files
    data_2024 = analyze_csv_file(file_2024)
    data_2025 = analyze_csv_file(file_2025)
    
    if 'error' in data_2024:
        logger.error(f"❌ 2024 analysis failed: {data_2024['error']}")
        return
        
    if 'error' in data_2025:
        logger.error(f"❌ 2025 analysis failed: {data_2025['error']}")
        return
    
    # Compare results
    logger.info(f"\n📊 Data Comparison for ISO Week 35:")
    logger.info(f"   📅 2024 ({file_2024.name}):")
    logger.info(f"      Total Installs: {data_2024['total_installs']:,}")
    logger.info(f"      Row Count: {data_2024['row_count']}")
    logger.info(f"      Media Sources: {len(data_2024['media_sources'])}")
    
    logger.info(f"   📅 2025 ({file_2025.name}):")
    logger.info(f"      Total Installs: {data_2025['total_installs']:,}")
    logger.info(f"      Row Count: {data_2025['row_count']}")
    logger.info(f"      Media Sources: {len(data_2025['media_sources'])}")
    
    # Check for differences
    install_diff = data_2025['total_installs'] - data_2024['total_installs']
    
    if data_2025['total_installs'] == data_2024['total_installs']:
        logger.warning("⚠️ WARNING: Identical install totals - may be wrong data!")
    else:
        percent_change = (install_diff / data_2024['total_installs'] * 100) if data_2024['total_installs'] > 0 else 0
        logger.info(f"   📈 YoY Change: {install_diff:+,} ({percent_change:+.1f}%)")
        logger.info("   ✅ Data shows real differences")
    
    # Compare top media sources
    logger.info(f"\n📱 Top Media Sources Comparison:")
    
    logger.info(f"   2024 Top 5:")
    for source, installs in list(data_2024['media_sources'].items())[:5]:
        logger.info(f"      {source}: {installs:,}")
    
    logger.info(f"   2025 Top 5:")
    for source, installs in list(data_2025['media_sources'].items())[:5]:
        logger.info(f"      {source}: {installs:,}")
    
    # Check for unified attribution evidence
    skan_indicators = ['skan', 'att', 'ios14', 'unified']
    traditional_indicators = ['traditional', 'deterministic']
    
    all_sources_2024 = set(data_2024['media_sources'].keys())
    all_sources_2025 = set(data_2025['media_sources'].keys())
    
    logger.info(f"\n🔍 Unified Attribution Check:")
    
    skan_found = any(any(indicator in source.lower() for indicator in skan_indicators) for source in all_sources_2025)
    traditional_found = any(any(indicator in source.lower() for indicator in traditional_indicators) for source in all_sources_2025)
    
    if skan_found or traditional_found:
        logger.info("   ✓ Unified attribution indicators found")
    else:
        logger.info("   - No obvious SKAN/Traditional indicators in source names")
        logger.info("   📝 This may be expected if attribution is unified at backend level")
    
    # File size check
    size_2024 = file_2024.stat().st_size
    size_2025 = file_2025.stat().st_size
    
    logger.info(f"\n📦 File Size Comparison:")
    logger.info(f"   2024: {size_2024:,} bytes")
    logger.info(f"   2025: {size_2025:,} bytes") 
    logger.info(f"   Difference: {size_2025 - size_2024:+,} bytes")
    
    if size_2024 != size_2025:
        logger.info("   ✅ Different file sizes confirm different data")
    
    return {
        '2024': data_2024,
        '2025': data_2025,
        'differences_found': data_2024['total_installs'] != data_2025['total_installs']
    }

if __name__ == "__main__":
    compare_unified_data()