# GitHub Actions Setup Guide

## Required GitHub Secrets

To enable automated weekly reports, you need to configure the following secrets in your GitHub repository:

### 1. Navigate to Repository Settings
- Go to your GitHub repository
- Click on **Settings** tab
- In the left sidebar, click **Secrets and variables** → **Actions**

### 2. Add Repository Secrets

Click **New repository secret** for each of the following:

#### Amplitude API Credentials
- **Name**: `AMPLITUDE_API_KEY`
- **Value**: `5f6f561c9df15cb3de99c79d53cbfe2c`

- **Name**: `AMPLITUDE_SECRET_KEY`  
- **Value**: `72425612322d26b7fb2ff912c4e6aae4`

#### Slack Integration
- **Name**: `SLACK_WEBHOOK_URL`
- **Value**: `https://hooks.slack.com/services/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`

#### GA4 Configuration
- **Name**: `GA4_WEB_PROPERTY_ID`
- **Value**: `330311466`

- **Name**: `GA4_APP_PROPERTY_ID`
- **Value**: `158472024`

#### GA4 Service Account JSON
- **Name**: `GA4_SERVICE_ACCOUNT_JSON`
- **Value**: Copy the entire contents of your `ga4_service_account/thortful-9a7a7-04cd279e1017.json` file
  
  To get this value:
  1. Open the file `ga4_service_account/thortful-9a7a7-04cd279e1017.json`
  2. Copy the entire JSON content (from the opening `{` to the closing `}`)
  3. Paste it as the secret value

## Schedule Configuration

The workflow is configured to run:
- **Every Monday at 9:00 AM UTC**
- Can also be triggered manually via GitHub Actions tab

## Testing the Setup

1. After adding all secrets, go to the **Actions** tab in your repository
2. Find the "Weekly Amplitude Analysis Report" workflow  
3. Click **Run workflow** to test manually
4. Check the workflow logs to ensure everything runs successfully

## Timezone Considerations

- The workflow runs at 9:00 AM UTC (Monday)
- Adjust the cron expression in `.github/workflows/weekly-report.yml` if you need a different time:
  - `0 9 * * 1` = 9:00 AM UTC Monday
  - `0 14 * * 1` = 2:00 PM UTC Monday (9:00 AM EST)
  - `0 16 * * 1` = 4:00 PM UTC Monday (9:00 AM PST)

## What Happens When It Runs

1. Fetches data from Amplitude and GA4 APIs
2. Generates analysis report 
3. Sends Slack notification with results
4. Commits updated `weekly_analysis.json` and `weekly_summary.txt` to repository
5. Updates are automatically pushed back to the main branch

## Troubleshooting

- Check the **Actions** tab for workflow execution logs
- Ensure all secrets are properly configured
- Verify GA4 service account JSON is valid
- Test Slack webhook URL is working

## Free Usage Limits

GitHub Actions provides 2,000 free minutes per month, which is more than sufficient for this weekly report (each run takes ~2-3 minutes).