# Infrastructure Deployment

This directory contains Bicep templates for deploying Event Kit to Azure.

## Resources Created

- **App Service Plan**: Linux-based hosting (B1 for dev, P1v3 for prod)
- **App Service**: Web App for Containers running the Event Kit agent
- **Application Insights**: Telemetry and monitoring
- **Log Analytics Workspace**: Centralized logging
- **Key Vault**: Secure storage for Graph API credentials and API tokens
- **Storage Account**: Persistent storage for exports and logs (blob containers)

## Prerequisites

1. Azure CLI installed and authenticated
2. Resource group created
3. Docker image published to Docker Hub or Azure Container Registry

## Deployment

### Development Environment

```bash
# Create resource group
az group create --name rg-eventkit-dev --location eastus

# Deploy infrastructure
az deployment group create \
  --resource-group rg-eventkit-dev \
  --template-file main.bicep \
  --parameters dev.bicepparam \
  --parameters graphTenantId="<your-tenant-id>" \
  --parameters graphClientId="<your-client-id>" \
  --parameters graphClientSecret="<your-client-secret>" \
  --parameters graphUserId="user@example.com"
```

### Production Environment

```bash
# Create resource group
az group create --name rg-eventkit-prod --location eastus

# Deploy infrastructure
az deployment group create \
  --resource-group rg-eventkit-prod \
  --template-file main.bicep \
  --parameters prod.bicepparam \
  --parameters graphTenantId="<your-tenant-id>" \
  --parameters graphClientId="<your-client-id>" \
  --parameters graphClientSecret="<your-client-secret>" \
  --parameters graphUserId="user@example.com" \
  --parameters apiToken="<your-api-token>"
```

## Outputs

After deployment, the template outputs:

- `appServiceUrl`: Public URL of the deployed agent
- `appServiceName`: Name of the App Service resource
- `appInsightsConnectionString`: Connection string for Application Insights
- `keyVaultName`: Name of the Key Vault
- `storageAccountName`: Name of the Storage Account

Access outputs:

```bash
az deployment group show \
  --resource-group rg-eventkit-dev \
  --name main \
  --query properties.outputs
```

## Updating Configuration

After deployment, update App Service settings:

```bash
# Update environment variable
az webapp config appsettings set \
  --resource-group rg-eventkit-dev \
  --name <app-service-name> \
  --settings GRAPH_USER_ID="newuser@example.com"
```

## Monitoring

View Application Insights in Azure Portal:

1. Navigate to Application Insights resource
2. View **Live Metrics** for real-time monitoring
3. Check **Failures** for error tracking
4. Use **Performance** tab for request analytics
5. Query logs in **Logs** section using KQL

## Scaling

Update App Service Plan SKU:

```bash
# Scale to higher tier
az appservice plan update \
  --resource-group rg-eventkit-prod \
  --name asp-eventkit-prod-<suffix> \
  --sku P2v3
```

## Cleanup

Delete all resources:

```bash
az group delete --name rg-eventkit-dev --yes --no-wait
```
