# Safe Development Guide

## Current Setup
- **Working Branch**: `main` (DO NOT modify directly)
- **Development Branch**: `development-iteration` (safe for experiments)
- **Remote**: Working production code that runs weekly via GitHub Actions

## Safe Development Workflow

### 1. Always Work on Development Branch
```bash
# Ensure you're on development branch
git checkout development-iteration

# Verify current branch
git branch --show-current
```

### 2. Never Push to Remote Without Testing
```bash
# DO NOT run these commands unless explicitly ready:
# git push origin main
# git push origin development-iteration
```

### 3. Test Locally First
```bash
# Test the analyzer locally
python3 amplitude_analyzer.py

# Check for syntax errors
python3 -m py_compile *.py

# Run with test parameters if needed
python3 test_local.py  # Create test scripts separately
```

### 4. Create Backup Before Major Changes
```bash
# Create timestamped backup
cp amplitude_analyzer.py amplitude_analyzer_backup_$(date +%Y%m%d_%H%M%S).py
```

### 5. Safe Merge Process (When Ready)
```bash
# 1. First, ensure development branch is clean
git status

# 2. Switch to main and pull latest
git checkout main
git pull origin main

# 3. Create a feature branch from main
git checkout -b feature/your-feature-name

# 4. Cherry-pick tested changes
git cherry-pick <commit-hash>

# 5. Test again on feature branch
python3 amplitude_analyzer.py

# 6. Only then create PR or merge
```

## Testing Strategies

### 1. Dry Run Mode
Create a test wrapper that doesn't send to Slack:
```python
# test_local.py
import os
os.environ['SLACK_WEBHOOK_URL'] = ''  # Disable Slack
os.environ['TEST_MODE'] = 'true'

from amplitude_analyzer import AmplitudeAnalyzer
analyzer = AmplitudeAnalyzer()
# Run analysis without side effects
```

### 2. Mock Data Testing
Use existing sample files:
- `sample_weekly_analysis.json`
- `sample_weekly_summary.txt`
- `mock_ga4_report.py`

### 3. Date Range Testing
Test with specific weeks to avoid affecting current data:
```python
# Test with old week that won't interfere
target_week = 20  # Week from earlier in year
```

## What NOT to Do

1. **Never force push**: `git push -f` is forbidden
2. **Never commit credentials**: Check `.env` is in `.gitignore`
3. **Never modify production branch directly**: Always use feature branches
4. **Never skip testing**: Always run locally first
5. **Never push untested GitHub Actions changes**: Test workflow syntax first

## Recovery Options

### If Something Goes Wrong Locally
```bash
# Reset to match remote main
git checkout main
git fetch origin
git reset --hard origin/main
git checkout development-iteration
git rebase main
```

### If Wrong Code Gets Pushed
1. DO NOT try to fix on main directly
2. Create a hotfix branch from main
3. Revert the problematic commit
4. Test thoroughly
5. Create PR for review

## Environment Isolation

### Development .env
Create `.env.development` for testing:
```
AMPLITUDE_API_KEY=your_test_key
AMPLITUDE_SECRET_KEY=your_test_secret
SLACK_WEBHOOK_URL=  # Empty to prevent sends
GA4_ENABLED=false   # Disable if testing Amplitude only
TEST_MODE=true
```

### Load Test Environment
```python
from dotenv import load_dotenv
load_dotenv('.env.development')  # Use test config
```

## Iteration Best Practices

1. **Small Changes**: Make incremental changes, test each
2. **Version Control**: Commit often with clear messages
3. **Document Changes**: Update comments and docs
4. **Test Edge Cases**: Empty data, API failures, etc.
5. **Keep Backups**: Save working versions before major refactors

## GitHub Actions Safety

The production workflow runs automatically. To test changes:

1. Create `.github/workflows/test-weekly-report.yml`
2. Use `workflow_dispatch` for manual testing
3. Set to run on development branch only
4. Use different job names to avoid conflicts

Remember: The remote `main` branch has working code that runs every Monday. Your goal is to improve without breaking this proven functionality.