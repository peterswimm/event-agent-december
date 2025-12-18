# Microsoft Foundry Deployment Guide

**Updated**: December 18, 2025  
**Version**: 1.0.0  
**Status**: Production Ready

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Step 1: Deploy Foundry Infrastructure](#step-1-deploy-foundry-infrastructure)
4. [Step 2: Configure Agent Framework](#step-2-configure-agent-framework)
5. [Step 3: Deploy Prompt Flow](#step-3-deploy-prompt-flow)
6. [Step 4: Test and Validate](#step-4-test-and-validate)
7. [Step 5: Production Deployment](#step-5-production-deployment)
8. [Monitoring and Operations](#monitoring-and-operations)
9. [Troubleshooting](#troubleshooting)

---

## Overview

This guide walks through deploying EventKit Agent to Microsoft Foundry (formerly Azure AI Foundry), enabling:

- **AI Hub and Project**: Centralized management for AI resources
- **Model Deployments**: GPT-4o, GPT-3.5-turbo, and custom models
- **Agent Framework**: Production-ready agent orchestration
- **Prompt Flow**: Visual workflow design and evaluation
- **Managed Compute**: Scalable serverless compute
- **Enterprise Security**: RBAC, Key Vault, Private Endpoints

---

## Prerequisites

### Required Tools

```bash
# Azure CLI
az version  # Requires 2.55.0+

# Azure ML Extension
az extension add -n ml

# Python 3.11+
python --version

# Agent Framework SDK (with --pre flag required)
pip install agent-framework-azure-ai --pre
pip install promptflow promptflow-azure
```

### Azure Permissions

- **Owner** or **Contributor** role on subscription
- **AI Administrator** role for Foundry resources
- **Key Vault Administrator** for secrets management

### Required Information

- Azure Subscription ID
- Resource Group name
- Preferred Azure region (eastus, westus, etc.)
- Bot ID and Password (if deploying Teams bot)

---

## Step 1: Deploy Foundry Infrastructure

### 1.1 Set Environment Variables

```bash
# Core settings
$SUBSCRIPTION_ID="your-subscription-id"
$RESOURCE_GROUP="eventkit-foundry-rg"
$LOCATION="eastus"
$ENVIRONMENT="prod"

# Foundry-specific
$DEPLOY_FOUNDRY="true"
$OPENAI_RESOURCE_NAME="eventkit-openai"

# Login to Azure
az login
az account set --subscription $SUBSCRIPTION_ID
```

### 1.2 Create Resource Group

```bash
az group create `
  --name $RESOURCE_GROUP `
  --location $LOCATION
```

### 1.3 Deploy with Bicep Template

```bash
# Deploy full infrastructure with Foundry resources
az deployment group create `
  --resource-group $RESOURCE_GROUP `
  --template-file infra/main.bicep `
  --parameters `
    environment=$ENVIRONMENT `
    location=$LOCATION `
    deployFoundry=true `
    openAIResourceName=$OPENAI_RESOURCE_NAME `
  --verbose
```

**Expected resources created**:
- AI Hub (`eventkit-prod-*-hub`)
- AI Project (`eventkit-prod-*-project`)
- AI Services (Cognitive Services)
- Azure OpenAI resource
- App Service, Key Vault, Storage, App Insights

### 1.4 Capture Deployment Outputs

```bash
# Get deployment outputs
$DEPLOYMENT_OUTPUT = az deployment group show `
  --resource-group $RESOURCE_GROUP `
  --name main `
  --query properties.outputs `
  | ConvertFrom-Json

# Extract key values
$AI_PROJECT_NAME = $DEPLOYMENT_OUTPUT.aiProjectName.value
$AI_PROJECT_ENDPOINT = $DEPLOYMENT_OUTPUT.aiProjectEndpoint.value
$AI_HUB_NAME = $DEPLOYMENT_OUTPUT.aiHubName.value

Write-Host "AI Project: $AI_PROJECT_NAME"
Write-Host "Endpoint: $AI_PROJECT_ENDPOINT"
```

---

## Step 2: Configure Agent Framework

### 2.1 Install Agent Framework SDK

```bash
# Install with --pre flag (required while in preview)
pip install agent-framework-azure-ai --pre

# Verify installation
python -c "from agent_framework_azure_ai import AzureAIAgent; print('✓ Agent Framework installed')"
```

### 2.2 Set Environment Variables

Create `.env` file or set environment variables:

```bash
# Microsoft Foundry Configuration
$env:FOUNDRY_PROJECT_ENDPOINT="https://$LOCATION.api.azureml.ms"
$env:FOUNDRY_SUBSCRIPTION_ID=$SUBSCRIPTION_ID
$env:FOUNDRY_RESOURCE_GROUP=$RESOURCE_GROUP
$env:FOUNDRY_PROJECT_NAME=$AI_PROJECT_NAME
$env:FOUNDRY_MODEL_DEPLOYMENT="gpt-4o"
$env:FOUNDRY_ENABLED="true"

# Azure Authentication
$env:AZURE_CLIENT_ID="your-app-registration-client-id"
$env:AZURE_CLIENT_SECRET="your-client-secret"
$env:AZURE_TENANT_ID="your-tenant-id"

# Or use Azure CLI credentials (recommended for local dev)
az login
```

### 2.3 Test Agent Framework Connection

```python
# test_foundry.py
from agent_framework_adapter import EventKitAgentFramework
from azure.identity import DefaultAzureCredential

async def test_connection():
    agent = EventKitAgentFramework(
        project_endpoint="https://eastus.api.azureml.ms",
        credential=DefaultAzureCredential(),
        model_deployment="gpt-4o"
    )
    
    response = await agent.run("recommend sessions about agents and AI")
    print(f"Response: {response}")

# Run test
import asyncio
asyncio.run(test_connection())
```

Run test:
```bash
python test_foundry.py
```

**Expected output**: Agent returns session recommendations

---

## Step 3: Deploy Prompt Flow

### 3.1 Install Prompt Flow SDK

```bash
pip install promptflow promptflow-azure
```

### 3.2 Connect to Foundry Project

```bash
# Configure prompt flow to use your project
pf config set connection.provider=azureml

# Set workspace details
az ml workspace show `
  --name $AI_PROJECT_NAME `
  --resource-group $RESOURCE_GROUP `
  --subscription $SUBSCRIPTION_ID
```

### 3.3 Create Azure OpenAI Connection

```bash
# Get OpenAI endpoint and key
$OPENAI_ENDPOINT = az cognitiveservices account show `
  --name $OPENAI_RESOURCE_NAME `
  --resource-group $RESOURCE_GROUP `
  --query properties.endpoint `
  --output tsv

# Create connection in Foundry
az ml connection create `
  --workspace-name $AI_PROJECT_NAME `
  --resource-group $RESOURCE_GROUP `
  --file - <<EOF
name: azure_openai_connection
type: azure_open_ai
api_base: $OPENAI_ENDPOINT
api_type: azure
api_version: 2024-02-01
EOF
```

### 3.4 Deploy EventKit Flow

```bash
# Navigate to project directory
cd d:\code\event-agent-example

# Test flow locally
pf flow test --flow flow.dag.yaml --inputs user_message="recommend AI sessions"

# Deploy to Foundry
pf flow create `
  --flow flow.dag.yaml `
  --workspace-name $AI_PROJECT_NAME `
  --resource-group $RESOURCE_GROUP `
  --subscription $SUBSCRIPTION_ID
```

### 3.5 Create Flow Deployment

```bash
# Deploy as managed endpoint
az ml online-deployment create `
  --name eventkit-flow-v1 `
  --endpoint-name eventkit-endpoint `
  --workspace-name $AI_PROJECT_NAME `
  --resource-group $RESOURCE_GROUP `
  --file - <<EOF
name: eventkit-flow-v1
endpoint_name: eventkit-endpoint
model: azureml:eventkit-flow:1
instance_type: Standard_DS3_v2
instance_count: 1
environment_variables:
  FOUNDRY_ENABLED: "true"
EOF
```

---

## Step 4: Test and Validate

### 4.1 Test Flow Endpoint

```bash
# Get endpoint URI
$ENDPOINT_URI = az ml online-endpoint show `
  --name eventkit-endpoint `
  --workspace-name $AI_PROJECT_NAME `
  --resource-group $RESOURCE_GROUP `
  --query scoring_uri `
  --output tsv

# Get endpoint key
$ENDPOINT_KEY = az ml online-endpoint get-credentials `
  --name eventkit-endpoint `
  --workspace-name $AI_PROJECT_NAME `
  --resource-group $RESOURCE_GROUP `
  --query primaryKey `
  --output tsv

# Test request
$body = @{
    user_message = "I'm interested in AI agents and machine learning"
    interests = "agents, ml"
} | ConvertTo-Json

Invoke-RestMethod -Uri $ENDPOINT_URI `
  -Method Post `
  -Headers @{
    "Authorization" = "Bearer $ENDPOINT_KEY"
    "Content-Type" = "application/json"
  } `
  -Body $body
```

### 4.2 Run Evaluation Flow

```bash
# Deploy evaluation flow
pf flow create `
  --flow flows/evaluation/flow.dag.yaml `
  --workspace-name $AI_PROJECT_NAME `
  --resource-group $RESOURCE_GROUP

# Run evaluation with test dataset
pf run create `
  --flow flows/evaluation/flow.dag.yaml `
  --data test_data.jsonl `
  --stream `
  --workspace-name $AI_PROJECT_NAME
```

### 4.3 View Metrics in Foundry Studio

```bash
# Open Foundry Studio
az ml workspace show `
  --name $AI_PROJECT_NAME `
  --query studio_endpoint `
  --output tsv
```

Navigate to:
1. **Prompt Flow** → **Runs** → View evaluation results
2. **Metrics** → Check precision, recall, F1 score
3. **Traces** → Debug flow execution

---

## Step 5: Production Deployment

### 5.1 Configure Production Settings

Update `infra/prod.bicepparam`:

```bicep
using 'main.bicep'

param environment = 'prod'
param deployFoundry = true
param openAIResourceName = 'eventkit-openai-prod'

// Scale settings for production
param appServiceSku = 'P1v3'
param openAIModelCapacity = 100  // Higher capacity
param enablePrivateEndpoint = true
```

### 5.2 Deploy Production Environment

```bash
az deployment group create `
  --resource-group eventkit-prod-rg `
  --template-file infra/main.bicep `
  --parameters infra/prod.bicepparam
```

### 5.3 Configure Auto-scaling

```bash
az ml online-endpoint update `
  --name eventkit-endpoint `
  --workspace-name $AI_PROJECT_NAME `
  --resource-group $RESOURCE_GROUP `
  --set `
    autoscale_enabled=true `
    autoscale_min_instances=2 `
    autoscale_max_instances=10
```

### 5.4 Enable Private Endpoints (Optional)

```bash
# Create private endpoint for AI Project
az ml workspace private-endpoint create `
  --workspace-name $AI_PROJECT_NAME `
  --resource-group $RESOURCE_GROUP `
  --private-endpoint-name eventkit-pe `
  --subnet-id /subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.Network/virtualNetworks/vnet/subnets/subnet
```

---

## Monitoring and Operations

### Application Insights Integration

```bash
# Get App Insights connection string
$APP_INSIGHTS_CONN = az deployment group show `
  --resource-group $RESOURCE_GROUP `
  --name main `
  --query properties.outputs.appInsightsConnectionString.value `
  --output tsv

# Configure in environment
$env:APPLICATIONINSIGHTS_CONNECTION_STRING=$APP_INSIGHTS_CONN
```

### View Logs and Metrics

```bash
# View flow execution logs
az ml job stream --name <job-name> `
  --workspace-name $AI_PROJECT_NAME `
  --resource-group $RESOURCE_GROUP

# Query Application Insights
az monitor app-insights query `
  --app $AI_PROJECT_NAME `
  --analytics-query "
    traces
    | where message contains 'EventKit'
    | order by timestamp desc
    | take 100
  "
```

### Set Up Alerts

```bash
# Create alert for high error rate
az monitor metrics alert create `
  --name high-error-rate `
  --resource-group $RESOURCE_GROUP `
  --scopes $ENDPOINT_ID `
  --condition "avg requests/failed > 10" `
  --window-size 5m `
  --evaluation-frequency 1m
```

---

## Troubleshooting

### Issue 1: Agent Framework Import Error

**Error**: `ModuleNotFoundError: No module named 'agent_framework_azure_ai'`

**Solution**:
```bash
# Ensure --pre flag is used
pip uninstall agent-framework-azure-ai
pip install agent-framework-azure-ai --pre
```

### Issue 2: Authentication Failed

**Error**: `AuthenticationError: Unable to authenticate with Azure`

**Solutions**:
```bash
# Option 1: Use Azure CLI login
az login
az account show

# Option 2: Use Service Principal
$env:AZURE_CLIENT_ID="..."
$env:AZURE_CLIENT_SECRET="..."
$env:AZURE_TENANT_ID="..."

# Option 3: Use Managed Identity (in Azure)
# No configuration needed - automatically works
```

### Issue 3: Model Not Found

**Error**: `ModelNotFound: Deployment 'gpt-4o' not found`

**Solution**:
```bash
# List available deployments
az cognitiveservices account deployment list `
  --name $OPENAI_RESOURCE_NAME `
  --resource-group $RESOURCE_GROUP

# Create deployment if missing
az cognitiveservices account deployment create `
  --name $OPENAI_RESOURCE_NAME `
  --resource-group $RESOURCE_GROUP `
  --deployment-name gpt-4o `
  --model-name gpt-4o `
  --model-version "2024-08-06" `
  --model-format OpenAI `
  --sku-capacity 30 `
  --sku-name Standard
```

### Issue 4: Flow Execution Timeout

**Error**: `TimeoutError: Flow execution exceeded timeout`

**Solution**:
```yaml
# In flow.dag.yaml, increase timeout
nodes:
  - name: generate_response
    timeout: 120  # Increase from default 30s
```

### Issue 5: Connection String Invalid

**Error**: `InvalidConnectionString: Unable to parse Foundry connection string`

**Solution**:
```bash
# Get correct connection string format
az ml workspace show `
  --name $AI_PROJECT_NAME `
  --resource-group $RESOURCE_GROUP `
  --query id `
  --output tsv

# Format: HostName=<region>.api.azureml.ms;SubscriptionId=<sub>;ResourceGroup=<rg>;ProjectName=<project>
```

---

## Cost Management

### Estimated Monthly Costs (Production)

| Resource | SKU | Estimated Cost |
|----------|-----|----------------|
| AI Hub | Basic | $0 (no charge) |
| AI Project | Basic | $0 (no charge) |
| Azure OpenAI (GPT-4o) | Standard, 30K TPM | $150-300 |
| App Service | P1v3 | $150 |
| Storage | Standard LRS | $25 |
| Application Insights | Pay-as-you-go | $50 |
| **Total** | | **~$375-525/month** |

### Cost Optimization Tips

1. **Use Reserved Capacity**: Save 30% on OpenAI with 1-year reservation
2. **Scale Down Dev/Test**: Use B1 App Service tier for non-prod ($13/month)
3. **Limit Model Capacity**: Start with 10K TPM, scale up as needed
4. **Enable Auto-shutdown**: Shut down compute during off-hours

---

## Next Steps

1. ✅ **Teams Integration**: Deploy bot to Teams using [docs/agents-sdk-setup.md](agents-sdk-setup.md)
2. ✅ **CI/CD Pipeline**: Automate deployments with GitHub Actions
3. ✅ **Custom Models**: Fine-tune models for your event data
4. ✅ **Multi-Region**: Deploy to multiple regions for high availability
5. ✅ **A/B Testing**: Test different models and prompts with traffic splitting

---

## Additional Resources

- **Microsoft Foundry Documentation**: https://learn.microsoft.com/azure/ai-studio/
- **Agent Framework GitHub**: https://github.com/microsoft/agent-framework
- **Prompt Flow Guide**: https://learn.microsoft.com/azure/machine-learning/prompt-flow/
- **Azure OpenAI Service**: https://learn.microsoft.com/azure/ai-services/openai/

---

**Last Updated**: December 18, 2025  
**Documentation Version**: 1.0.0  
**Status**: Production Ready ✅
