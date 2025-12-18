using './main.bicep'

// Development environment parameters
param environment = 'dev'
param location = 'eastus'
param imageTag = 'dev'

// Graph API credentials (optional - set in deployment command)
param graphTenantId = ''
param graphClientId = ''
param graphClientSecret = ''
param graphUserId = ''

// API token (optional)
param apiToken = ''

// Container registry (optional - uses Docker Hub if empty)
param containerRegistry = ''
