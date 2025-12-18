using './main.bicep'

// Production environment parameters
param environment = 'prod'
param location = 'eastus'
param imageTag = 'latest'

// Graph API credentials (set via secure parameters in deployment)
param graphTenantId = ''
param graphClientId = ''
param graphClientSecret = ''
param graphUserId = ''

// API token (set via secure parameters in deployment)
param apiToken = ''

// Container registry (recommended for production)
param containerRegistry = ''
