# Environment Setup for Staging/Production Deployments

## GitHub Environments Configuration

### 1. Staging Environment
**Purpose:** Test enhanced weekly analyzer on development-iteration branch
**Slack Channel:** Test webhook
**Schedule:** Monday 8 AM (1 hour after production for comparison)

### 2. Production Environment  
**Purpose:** Run proven enhanced weekly analyzer on main branch
**Slack Channel:** Production webhook
**Schedule:** Monday 7 AM (existing schedule)

## Required Environment Variables

### GitHub Secrets (both staging and production)
Set these in GitHub → Settings → Environments → [staging/production] → Secrets:

```
AMPLITUDE_API_KEY=your_amplitude_api_key
AMPLITUDE_SECRET_KEY=your_amplitude_secret_key
GA4_SERVICE_ACCOUNT_JSON={"type":"service_account",...}
GA4_WEB_PROPERTY_ID=your_web_property_id
GA4_APP_PROPERTY_ID=158472024
APPSFLYER_USERNAME=your_appsflyer_email
APPSFLYER_PASSWORD=your_appsflyer_password
APPSFLYER_API_TOKEN=your_api_token
APPSFLYER_APP_ID=your_app_id
```

### GitHub Variables (environment-specific)
Set these in GitHub → Settings → Environments → [environment] → Variables:

**Staging:**
```
STAGING_SLACK_WEBHOOK_URL=https://hooks.slack.com/services/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
```

**Production:**
```
PRODUCTION_SLACK_WEBHOOK_URL=your_production_slack_webhook
```

## Workflow Overview

### Staging Workflow (`staging-enhanced-weekly.yml`)
- **Trigger:** Push to development-iteration branch + manual + Monday 8 AM
- **Environment:** staging
- **Slack:** Test channel
- **Purpose:** Validate enhanced analyzer before production

### Production Workflow (`production-enhanced-weekly.yml`)
- **Trigger:** Push to main branch + Monday 7 AM  
- **Environment:** production
- **Slack:** Production channel
- **Purpose:** Live weekly reports

### Original Workflow (`weekly-report.yml`)
- **Status:** Updated to use enhanced analyzer
- **Can be deprecated** once production workflow is proven

## Deployment Flow

```
development-iteration → staging environment → test results → merge to main → production environment
```

## Next Steps

1. **Set up environment variables** in GitHub
2. **Push workflows to remote**
3. **Run staging test** on development branch
4. **Review staging results** in test Slack channel
5. **Merge to main** after successful staging test
6. **Production runs automatically** every Monday

This approach ensures safe testing while following the SAFE_DEVELOPMENT_GUIDE.md principles.