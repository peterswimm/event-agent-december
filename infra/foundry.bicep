// Azure AI Hub and Project Resources
// Microsoft Foundry (formerly Azure AI Foundry) integration

@description('Deploy Microsoft Foundry resources (AI Hub and Project)')
param deployFoundry bool = false

@description('Azure OpenAI resource name (if using Azure OpenAI)')
param openAIResourceName string = ''

@description('OpenAI model deployments')
param modelDeployments array = [
  {
    name: 'gpt-4o'
    model: {
      format: 'OpenAI'
      name: 'gpt-4o'
      version: '2024-08-06'
    }
    sku: {
      name: 'Standard'
      capacity: 30
    }
  }
  {
    name: 'gpt-35-turbo'
    model: {
      format: 'OpenAI'
      name: 'gpt-35-turbo'
      version: '0125'
    }
    sku: {
      name: 'Standard'
      capacity: 30
    }
  }
]

// AI Services (Cognitive Services multi-service account)
resource aiServices 'Microsoft.CognitiveServices/accounts@2023-10-01-preview' = if (deployFoundry) {
  name: '${appName}-aiservices'
  location: location
  kind: 'AIServices'
  sku: {
    name: 'S0'
  }
  properties: {
    customSubDomainName: '${appName}-aiservices'
    publicNetworkAccess: 'Enabled'
    networkAcls: {
      defaultAction: 'Allow'
    }
  }
}

// Azure OpenAI (optional - if using OpenAI models)
resource openAI 'Microsoft.CognitiveServices/accounts@2023-10-01-preview' = if (deployFoundry && !empty(openAIResourceName)) {
  name: openAIResourceName
  location: location
  kind: 'OpenAI'
  sku: {
    name: 'S0'
  }
  properties: {
    customSubDomainName: openAIResourceName
    publicNetworkAccess: 'Enabled'
  }
}

// OpenAI Model Deployments
resource openAIDeployments 'Microsoft.CognitiveServices/accounts/deployments@2023-10-01-preview' = [for deployment in modelDeployments: if (deployFoundry && !empty(openAIResourceName)) {
  parent: openAI
  name: deployment.name
  sku: deployment.sku
  properties: {
    model: deployment.model
    raiPolicyName: 'Microsoft.Default'
  }
}]

// Azure AI Hub (Machine Learning Workspace)
resource aiHub 'Microsoft.MachineLearningServices/workspaces@2024-04-01' = if (deployFoundry) {
  name: '${appName}-hub'
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  sku: {
    name: 'Basic'
    tier: 'Basic'
  }
  kind: 'Hub'
  properties: {
    friendlyName: 'EventKit AI Hub - ${environment}'
    description: 'Azure AI Hub for EventKit agent development and deployment'
    storageAccount: storageAccount.id
    keyVault: keyVault.id
    applicationInsights: appInsights.id
    publicNetworkAccess: 'Enabled'
    discoveryUrl: 'https://${location}.api.azureml.ms/discovery'
  }
}

// AI Hub Connections (to AI Services and OpenAI)
resource aiServicesConnection 'Microsoft.MachineLearningServices/workspaces/connections@2024-04-01' = if (deployFoundry) {
  parent: aiHub
  name: 'aiservices-connection'
  properties: {
    category: 'AIServices'
    target: aiServices.properties.endpoint
    authType: 'AAD'
    isSharedToAll: true
    metadata: {
      ApiVersion: '2024-02-01'
      ResourceId: aiServices.id
    }
  }
}

resource openAIConnection 'Microsoft.MachineLearningServices/workspaces/connections@2024-04-01' = if (deployFoundry && !empty(openAIResourceName)) {
  parent: aiHub
  name: 'openai-connection'
  properties: {
    category: 'AzureOpenAI'
    target: openAI.properties.endpoint
    authType: 'AAD'
    isSharedToAll: true
    metadata: {
      ApiVersion: '2024-02-01'
      ResourceId: openAI.id
      ApiType: 'Azure'
      DeploymentApiVersion: '2024-08-01-preview'
    }
  }
}

// Azure AI Project (ML Workspace linked to Hub)
resource aiProject 'Microsoft.MachineLearningServices/workspaces@2024-04-01' = if (deployFoundry) {
  name: '${appName}-project'
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  sku: {
    name: 'Basic'
    tier: 'Basic'
  }
  kind: 'Project'
  properties: {
    friendlyName: 'EventKit Project - ${environment}'
    description: 'Azure AI Project for EventKit agent deployment'
    hubResourceId: aiHub.id
    publicNetworkAccess: 'Enabled'
  }
}

// Grant AI Hub/Project access to Key Vault
resource aiHubKeyVaultAccess 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (deployFoundry) {
  name: guid(keyVault.id, aiHub.id, 'Key Vault Secrets User')
  scope: keyVault
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '4633458b-17de-408a-b874-0445c86b69e6')
    principalId: aiHub.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

resource aiProjectKeyVaultAccess 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (deployFoundry) {
  name: guid(keyVault.id, aiProject.id, 'Key Vault Secrets User')
  scope: keyVault
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '4633458b-17de-408a-b874-0445c86b69e6')
    principalId: aiProject.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

// Grant AI Hub/Project access to Storage
resource aiHubStorageAccess 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (deployFoundry) {
  name: guid(storageAccount.id, aiHub.id, 'Storage Blob Data Contributor')
  scope: storageAccount
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'ba92f5b4-2d11-453d-a403-e96b0029c9fe')
    principalId: aiHub.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

resource aiProjectStorageAccess 'Microsoft.Authorization/roleAssignments@2022-04-01' = if (deployFoundry) {
  name: guid(storageAccount.id, aiProject.id, 'Storage Blob Data Contributor')
  scope: storageAccount
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', 'ba92f5b4-2d11-453d-a403-e96b0029c9fe')
    principalId: aiProject.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

// Outputs for Foundry resources
output aiHubName string = deployFoundry ? aiHub.name : ''
output aiHubId string = deployFoundry ? aiHub.id : ''
output aiProjectName string = deployFoundry ? aiProject.name : ''
output aiProjectId string = deployFoundry ? aiProject.id : ''
output aiProjectEndpoint string = deployFoundry ? 'https://${location}.api.azureml.ms' : ''
output aiServicesEndpoint string = deployFoundry ? aiServices.properties.endpoint : ''
output openAIEndpoint string = deployFoundry && !empty(openAIResourceName) ? openAI.properties.endpoint : ''
