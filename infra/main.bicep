// Event Kit Infrastructure - Main Bicep Template
// Deploys: App Service, Application Insights, Key Vault, Storage Account

@description('Environment name (dev, staging, prod)')
@allowed(['dev', 'staging', 'prod'])
param environment string = 'dev'

@description('Location for all resources')
param location string = resourceGroup().location

@description('Unique suffix for resource names')
param resourceSuffix string = uniqueString(resourceGroup().id)

@description('Container image tag')
param imageTag string = 'latest'

@description('Container registry name (optional - uses Docker Hub if not provided)')
param containerRegistry string = ''

@description('Graph API Tenant ID')
@secure()
param graphTenantId string = ''

@description('Graph API Client ID')
@secure()
param graphClientId string = ''

@description('Graph API Client Secret')
@secure()
param graphClientSecret string = ''

@description('Graph API default user ID')
param graphUserId string = ''

@description('API token for authentication (optional)')
@secure()
param apiToken string = ''

// Variables
var appName = 'eventkit-${environment}-${resourceSuffix}'
var appServicePlanName = 'asp-${appName}'
var appInsightsName = 'ai-${appName}'
var keyVaultName = 'kv-${take(replace(appName, '-', ''), 24)}'
var storageAccountName = 'st${take(replace(appName, '-', ''), 20)}'
var logAnalyticsName = 'log-${appName}'

// Log Analytics Workspace
resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: logAnalyticsName
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
  }
}

// Application Insights
resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: appInsightsName
  location: location
  kind: 'web'
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalytics.id
    IngestionMode: 'LogAnalytics'
  }
}

// Storage Account
resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: storageAccountName
  location: location
  sku: {
    name: 'Standard_LRS'
  }
  kind: 'StorageV2'
  properties: {
    accessTier: 'Hot'
    supportsHttpsTrafficOnly: true
    minimumTlsVersion: 'TLS1_2'
  }
}

// Blob containers for exports and logs
resource blobServices 'Microsoft.Storage/storageAccounts/blobServices@2023-01-01' = {
  parent: storageAccount
  name: 'default'
}

resource exportsContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = {
  parent: blobServices
  name: 'exports'
  properties: {
    publicAccess: 'None'
  }
}

resource logsContainer 'Microsoft.Storage/storageAccounts/blobServices/containers@2023-01-01' = {
  parent: blobServices
  name: 'logs'
  properties: {
    publicAccess: 'None'
  }
}

// Key Vault
resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: keyVaultName
  location: location
  properties: {
    sku: {
      family: 'A'
      name: 'standard'
    }
    tenantId: subscription().tenantId
    enableRbacAuthorization: true
    enableSoftDelete: true
    softDeleteRetentionInDays: 7
  }
}

// Store secrets in Key Vault
resource graphTenantIdSecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = if (!empty(graphTenantId)) {
  parent: keyVault
  name: 'graph-tenant-id'
  properties: {
    value: graphTenantId
  }
}

resource graphClientIdSecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = if (!empty(graphClientId)) {
  parent: keyVault
  name: 'graph-client-id'
  properties: {
    value: graphClientId
  }
}

resource graphClientSecretSecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = if (!empty(graphClientSecret)) {
  parent: keyVault
  name: 'graph-client-secret'
  properties: {
    value: graphClientSecret
  }
}

resource apiTokenSecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = if (!empty(apiToken)) {
  parent: keyVault
  name: 'api-token'
  properties: {
    value: apiToken
  }
}

// App Service Plan (Linux)
resource appServicePlan 'Microsoft.Web/serverfarms@2023-01-01' = {
  name: appServicePlanName
  location: location
  kind: 'linux'
  sku: {
    name: environment == 'prod' ? 'P1v3' : 'B1'
    tier: environment == 'prod' ? 'PremiumV3' : 'Basic'
  }
  properties: {
    reserved: true
  }
}

// App Service (Web App for Containers)
resource appService 'Microsoft.Web/sites@2023-01-01' = {
  name: appName
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    serverFarmId: appServicePlan.id
    httpsOnly: true
    siteConfig: {
      linuxFxVersion: empty(containerRegistry) ? 'DOCKER|peterswimm/event-agent:${imageTag}' : 'DOCKER|${containerRegistry}.azurecr.io/event-agent:${imageTag}'
      alwaysOn: environment == 'prod'
      minTlsVersion: '1.2'
      ftpsState: 'Disabled'
      healthCheckPath: '/health'
      appSettings: [
        {
          name: 'APP_INSIGHTS_CONNECTION_STRING'
          value: appInsights.properties.ConnectionString
        }
        {
          name: 'GRAPH_TENANT_ID'
          value: !empty(graphTenantId) ? '@Microsoft.KeyVault(SecretUri=${graphTenantIdSecret.properties.secretUri})' : ''
        }
        {
          name: 'GRAPH_CLIENT_ID'
          value: !empty(graphClientId) ? '@Microsoft.KeyVault(SecretUri=${graphClientIdSecret.properties.secretUri})' : ''
        }
        {
          name: 'GRAPH_CLIENT_SECRET'
          value: !empty(graphClientSecret) ? '@Microsoft.KeyVault(SecretUri=${graphClientSecretSecret.properties.secretUri})' : ''
        }
        {
          name: 'GRAPH_USER_ID'
          value: graphUserId
        }
        {
          name: 'API_TOKEN'
          value: !empty(apiToken) ? '@Microsoft.KeyVault(SecretUri=${apiTokenSecret.properties.secretUri})' : ''
        }
        {
          name: 'WEBSITES_ENABLE_APP_SERVICE_STORAGE'
          value: 'false'
        }
        {
          name: 'DOCKER_ENABLE_CI'
          value: 'true'
        }
      ]
    }
  }
}

// Grant App Service managed identity access to Key Vault
resource keyVaultAccessPolicy 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(keyVault.id, appService.id, 'Key Vault Secrets User')
  scope: keyVault
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '4633458b-17de-408a-b874-0445c86b69e6') // Key Vault Secrets User
    principalId: appService.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

// Grant App Service access to Storage Account
resource storageAccessPolicy 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(storageAccount.id, appService.id, 'Storage Blob Data Contributor')
  scope: storageAccount
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'ba92f5b4-2d11-453d-a403-e96b0029c9fe') // Storage Blob Data Contributor
    principalId: appService.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

// Outputs
output appServiceUrl string = 'https://${appService.properties.defaultHostName}'
output appServiceName string = appService.name
output appInsightsConnectionString string = appInsights.properties.ConnectionString
output keyVaultName string = keyVault.name
output storageAccountName string = storageAccount.name
