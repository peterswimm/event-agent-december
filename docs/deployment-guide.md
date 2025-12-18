# Event Kit Agent - Production Deployment Guide

**Version**: 1.0.0  
**Last Updated**: December 18, 2025  
**Status**: Ready for Production

---

## 📋 Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Azure Infrastructure Setup](#azure-infrastructure-setup)
3. [Bot Service Configuration](#bot-service-configuration)
4. [Teams Deployment](#teams-deployment)
5. [Monitoring & Operations](#monitoring--operations)
6. [Rollback Procedures](#rollback-procedures)
7. [Performance Tuning](#performance-tuning)

---

## Pre-Deployment Checklist

### Prerequisites

- [ ] Azure subscription with Owner/Contributor access
- [ ] Azure CLI installed and authenticated
- [ ] Docker installed and running
- [ ] Bot Framework SDK packages installed
- [ ] All environment variables configured
- [ ] SSL certificate for HTTPS endpoint

### Security Review

- [ ] Security validator module tested and working
- [ ] Rate limiter configured (100 req/min/IP)
- [ ] CORS headers properly configured
- [ ] Bot password securely stored in Key Vault
- [ ] All secrets rotated in last 90 days
- [ ] Application Insights configured for logging

### Testing Completed

- [ ] Unit tests passing (`pytest tests/ -v`)
- [ ] Integration tests with bot handler
- [ ] Local testing with Bot Emulator
- [ ] Graph API integration tested (if enabled)
- [ ] Load testing completed
- [ ] Security testing completed

---

## Azure Infrastructure Setup

### Step 1: Deploy Infrastructure with Bicep

```bash
# Variables
RESOURCE_GROUP="eventkit-prod-rg"
LOCATION="eastus"
ENVIRONMENT="prod"

# Create resource group
az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION

# Deploy Bicep template
az deployment group create \
  --resource-group $RESOURCE_GROUP \
  --template-file infra/main.bicep \
  --parameters infra/prod.bicepparam \
  --parameters \
    environment=$ENVIRONMENT \
    location=$LOCATION \
    appServiceSku=P1v3 \
    storageAccountSku=Standard_GRS \
    logRetentionDays=90

# Get deployment outputs
DEPLOYMENT_OUTPUT=$(az deployment group show \
  --resource-group $RESOURCE_GROUP \
  --name main \
  --query properties.outputs)
```

### Step 2: Configure Key Vault Secrets

```bash
# Get Key Vault name from deployment output
KEY_VAULT_NAME=$(echo $DEPLOYMENT_OUTPUT | jq -r '.keyVaultName.value')

# Set secrets
az keyvault secret set \
  --vault-name $KEY_VAULT_NAME \
  --name "BotId" \
  --value "YOUR_BOT_ID"

az keyvault secret set \
  --vault-name $KEY_VAULT_NAME \
  --name "BotPassword" \
  --value "YOUR_BOT_PASSWORD"

az keyvault secret set \
  --vault-name $KEY_VAULT_NAME \
  --name "GraphTenantId" \
  --value "YOUR_TENANT_ID"

az keyvault secret set \
  --vault-name $KEY_VAULT_NAME \
  --name "GraphClientId" \
  --value "YOUR_CLIENT_ID"

az keyvault secret set \
  --vault-name $KEY_VAULT_NAME \
  --name "GraphClientSecret" \
  --value "YOUR_CLIENT_SECRET"

az keyvault secret set \
  --vault-name $KEY_VAULT_NAME \
  --name "AppInsightsConnectionString" \
  --value "YOUR_CONNECTION_STRING"
```

### Step 3: Configure Container Registry

```bash
# Create or use existing ACR
ACR_NAME="eventkitacr"
ACR_LOGIN_SERVER="${ACR_NAME}.azurecr.io"

# Get access key
ACR_USERNAME=$(az acr credential show \
  --name $ACR_NAME \
  --query username -o tsv)

ACR_PASSWORD=$(az acr credential show \
  --name $ACR_NAME \
  --query "passwords[0].value" -o tsv)

# Login to ACR
echo $ACR_PASSWORD | docker login \
  --username $ACR_USERNAME \
  --password-stdin \
  $ACR_LOGIN_SERVER
```

---

## Bot Service Configuration

### Step 1: Register Bot Service

```bash
# Create Bot Service resource
BOT_NAME="EventKit-Agent"
BOT_SERVICE_RG=$RESOURCE_GROUP

az bot create \
  --name $BOT_NAME \
  --resource-group $BOT_SERVICE_RG \
  --kind registration \
  --display-name "Event Kit Session Recommendation Agent" \
  --endpoint "https://${APP_SERVICE_URL}/api/messages" \
  --app-type MultiTenant

# Get bot ID and password
BOT_ID=$(az bot show \
  --name $BOT_NAME \
  --resource-group $BOT_SERVICE_RG \
  --query appId -o tsv)

echo "Bot ID: $BOT_ID"
echo "Save bot password to Key Vault"
```

### Step 2: Configure Bot Channels

**Enable Teams Channel:**
```bash
az bot channel create teams \
  --name $BOT_NAME \
  --resource-group $BOT_SERVICE_RG
```

**Enable Outlook Channel (Optional):**
```bash
az bot channel create outlook \
  --name $BOT_NAME \
  --resource-group $BOT_SERVICE_RG
```

### Step 3: Upload Teams Manifest

```bash
# Create zip package
zip -r eventkit-teams.zip \
  teams-app.json \
  assets/

# Upload to Teams
# Manual process in Teams Admin Center:
# 1. Go to Teams apps → Manage apps
# 2. Click "Upload a custom app"
# 3. Select eventkit-teams.zip
# 4. Configure permissions
# 5. Assign to teams/users
```

---

## Teams Deployment

### Step 1: Build and Push Docker Image

```bash
# Build Docker image
DOCKER_TAG="${ACR_LOGIN_SERVER}/eventkit:latest"
DOCKER_VERSION_TAG="${ACR_LOGIN_SERVER}/eventkit:v1.0.0"

docker build \
  -f deploy/Dockerfile \
  -t $DOCKER_TAG \
  -t $DOCKER_VERSION_TAG \
  .

# Push to ACR
docker push $DOCKER_TAG
docker push $DOCKER_VERSION_TAG
```

### Step 2: Deploy to App Service

```bash
# Get App Service name from deployment
APP_SERVICE_NAME=$(echo $DEPLOYMENT_OUTPUT | jq -r '.appServiceName.value')

# Configure container
az webapp config container set \
  --resource-group $RESOURCE_GROUP \
  --name $APP_SERVICE_NAME \
  --docker-custom-image-name $DOCKER_TAG \
  --docker-registry-server-url "https://${ACR_LOGIN_SERVER}" \
  --docker-registry-server-user $ACR_USERNAME \
  --docker-registry-server-password $ACR_PASSWORD

# Configure application settings
az webapp config appsettings set \
  --resource-group $RESOURCE_GROUP \
  --name $APP_SERVICE_NAME \
  --settings \
    WEBSITES_PORT=8010 \
    DOCKER_ENABLE_CI=true \
    BOT_ID="@Microsoft.KeyVault(SecretUri=https://${KEY_VAULT_NAME}.vault.azure.net/secrets/BotId/)" \
    BOT_PASSWORD="@Microsoft.KeyVault(SecretUri=https://${KEY_VAULT_NAME}.vault.azure.net/secrets/BotPassword/)"
```

### Step 3: Configure Custom Domain

```bash
# Add custom domain (if applicable)
CUSTOM_DOMAIN="eventkit-agent.example.com"

az webapp config hostname add \
  --resource-group $RESOURCE_GROUP \
  --webapp-name $APP_SERVICE_NAME \
  --hostname $CUSTOM_DOMAIN

# Configure SSL certificate
az webapp config ssl bind \
  --resource-group $RESOURCE_GROUP \
  --name $APP_SERVICE_NAME \
  --certificate-thumbprint <certificate-thumbprint> \
  --ssl-type SNI
```

### Step 4: Verify Deployment

```bash
# Get App Service URL
APP_SERVICE_URL=$(az webapp show \
  --resource-group $RESOURCE_GROUP \
  --name $APP_SERVICE_NAME \
  --query defaultHostName -o tsv)

# Test health endpoint
curl "https://${APP_SERVICE_URL}/health"

# Expected response:
# {"status":"ok","service":"EventKit Bot","port":8010}

# Test bot endpoint
curl -X POST "https://${APP_SERVICE_URL}/api/messages" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <token>" \
  -d '{
    "type": "message",
    "text": "test",
    "from": {"id": "user1"},
    "recipient": {"id": "bot"}
  }'
```

---

## Monitoring & Operations

### Application Insights Setup

```bash
# Get Application Insights instance
APPINSIGHTS_NAME=$(echo $DEPLOYMENT_OUTPUT | jq -r '.appInsightsName.value')

# Create query for agent calls
az monitor app-insights query \
  --app $APPINSIGHTS_NAME \
  --resource-group $RESOURCE_GROUP \
  --analytics-query "
    customEvents
    | where name startswith 'agent_'
    | summarize count() by name
    | order by count_ desc
  " \
  --timespan "PT24H"
```

### Alert Configuration

```bash
# Create alert for high error rate
az monitor metrics alert create \
  --resource-group $RESOURCE_GROUP \
  --name "EventKit-HighErrorRate" \
  --scopes "/subscriptions/${SUBSCRIPTION_ID}/resourceGroups/${RESOURCE_GROUP}/providers/Microsoft.Web/sites/${APP_SERVICE_NAME}" \
  --condition "avg(Http5xx) > 10" \
  --window-size 5m \
  --evaluation-frequency 1m \
  --severity 2 \
  --action "/subscriptions/${SUBSCRIPTION_ID}/resourceGroups/${RESOURCE_GROUP}/providers/microsoft.insights/actionGroups/EventKitAlerts"

# Create alert for bot errors
az monitor log-analytics query \
  --workspace "/subscriptions/${SUBSCRIPTION_ID}/resourceGroups/${RESOURCE_GROUP}/providers/microsoft.operationalinsights/workspaces/eventkit-law" \
  --analytics-query "
    customEvents
    | where name == 'agent_error'
    | summarize ErrorCount = count() by bin(timestamp, 5m)
    | where ErrorCount > 5
  "
```

### Logging & Diagnostics

```bash
# Enable diagnostic logging
az webapp log config \
  --resource-group $RESOURCE_GROUP \
  --name $APP_SERVICE_NAME \
  --docker-container-logging filesystem \
  --level verbose

# Stream logs
az webapp log tail \
  --resource-group $RESOURCE_GROUP \
  --name $APP_SERVICE_NAME \
  --provider docker

# Export logs to Log Analytics
az monitor diagnostic-settings create \
  --resource "/subscriptions/${SUBSCRIPTION_ID}/resourceGroups/${RESOURCE_GROUP}/providers/Microsoft.Web/sites/${APP_SERVICE_NAME}" \
  --name "EventKit-Diagnostics" \
  --workspace "/subscriptions/${SUBSCRIPTION_ID}/resourceGroups/${RESOURCE_GROUP}/providers/microsoft.operationalinsights/workspaces/eventkit-law" \
  --logs '[{"category":"AppServicePlatformLogs","enabled":true}]' \
  --metrics '[{"category":"AllMetrics","enabled":true}]'
```

---

## Rollback Procedures

### Automatic Rollback (if deployment fails)

```bash
# Rollback to previous image
PREVIOUS_IMAGE="${ACR_LOGIN_SERVER}/eventkit:v0.9.0"

az webapp config container set \
  --resource-group $RESOURCE_GROUP \
  --name $APP_SERVICE_NAME \
  --docker-custom-image-name $PREVIOUS_IMAGE \
  --docker-registry-server-url "https://${ACR_LOGIN_SERVER}" \
  --docker-registry-server-user $ACR_USERNAME \
  --docker-registry-server-password $ACR_PASSWORD

# Verify health
sleep 30
curl "https://${APP_SERVICE_URL}/health"
```

### Manual Rollback

```bash
# If health check fails, manually restart
az webapp restart \
  --resource-group $RESOURCE_GROUP \
  --name $APP_SERVICE_NAME

# Check App Service logs
az webapp log tail \
  --resource-group $RESOURCE_GROUP \
  --name $APP_SERVICE_NAME
```

---

## Performance Tuning

### App Service Scaling

```bash
# Scale up for production
az appservice plan update \
  --resource-group $RESOURCE_GROUP \
  --name eventkit-app-plan \
  --sku P1v3 \
  --number-of-workers 3

# Configure auto-scale
az monitor autoscale create \
  --resource-group $RESOURCE_GROUP \
  --resource eventkit-app-plan \
  --resource-type "Microsoft.Web/serverfarms" \
  --min-count 2 \
  --max-count 10 \
  --count 3
```

### Rate Limiting Configuration

```bash
# Update environment variables in App Service
az webapp config appsettings set \
  --resource-group $RESOURCE_GROUP \
  --name $APP_SERVICE_NAME \
  --settings \
    RATE_LIMIT_REQUESTS_PER_MINUTE=100 \
    RATE_LIMIT_WINDOW_SECONDS=60
```

### Caching Strategy

Enable Application-level caching:

```python
# In settings.py
CACHE_CONFIG = {
    "recommendations_ttl": 300,  # 5 minutes
    "graph_calendar_ttl": 600,   # 10 minutes
    "manifest_ttl": 3600          # 1 hour
}
```

---

## Post-Deployment Validation

```bash
# 1. Health check
curl -s "https://${APP_SERVICE_URL}/health" | jq .

# 2. Test recommendation flow
curl -X POST "https://${APP_SERVICE_URL}/api/messages" \
  --data-binary @- << 'EOF'
{
  "type": "message",
  "text": "recommend agents",
  "from": {"id": "user123", "name": "Test User"},
  "recipient": {"id": "bot", "name": "EventKit"},
  "id": "msg123"
}
EOF

# 3. Verify logs in Application Insights
az monitor app-insights query \
  --app $APPINSIGHTS_NAME \
  --resource-group $RESOURCE_GROUP \
  --analytics-query "
    traces
    | where timestamp > ago(5m)
    | order by timestamp desc
    | limit 20
  "

# 4. Check team's integration
# Manual: Test @bot commands in Teams
```

---

## Success Criteria

✅ Deployment successful when:
- [ ] Health endpoint returns 200 OK
- [ ] Bot responds to messages in Teams
- [ ] Recommendations return within 2 seconds
- [ ] Error rate < 0.1%
- [ ] All three tools working (recommend, explain, export)
- [ ] Application Insights logging events
- [ ] No critical alerts triggered

---

## Support & Escalation

| Issue | Contact | Response Time |
|-------|---------|---|
| Production outage | On-call Engineer | 15 min |
| Bot not responding | DevOps Team | 30 min |
| Performance degradation | Platform Team | 1 hour |
| Data/Security concern | Security Team | 2 hours |

---

**Deployment Date**: ___________  
**Deployed By**: ___________  
**Approval**: ___________
