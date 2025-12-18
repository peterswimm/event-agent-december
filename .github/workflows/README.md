# CI/CD Pipeline Documentation

This project uses GitHub Actions for continuous integration and deployment.

## Workflows

### 1. Tests (`test.yml`)
**Triggers**: Pull requests and pushes to `main` and `develop` branches

**What it does**:
- Sets up Python 3.11
- Installs dependencies from `requirements.txt` and `requirements-dev.txt`
- Runs pytest with coverage reporting
- Uploads coverage to Codecov (if token configured)
- Adds test summary to PR

**Required secrets**: None (uses mock Graph API credentials)

**Optional secrets**:
- `CODECOV_TOKEN` - For coverage reporting to Codecov

### 2. Lint (`lint.yml`)
**Triggers**: Pull requests and pushes to `main` and `develop` branches

**What it does**:
- Checks code formatting with Black
- Checks import sorting with isort
- Runs pylint on all Python files (continues on error)
- Adds lint summary to PR

**Required secrets**: None

### 3. Deploy (`deploy.yml`)
**Triggers**: 
- Pushes to `main` branch (auto-deploys to dev)
- Manual workflow dispatch (choose environment)

**What it does**:
1. **Build Job**:
   - Builds multi-stage Docker image
   - Pushes to GitHub Container Registry (ghcr.io)
   - Tags with branch name, SHA, and `latest`
   - Uses layer caching for faster builds

2. **Deploy Job**:
   - Logs in to Azure using OIDC (Workload Identity)
   - Deploys Bicep template to specified environment
   - Passes secrets to Bicep parameters
   - Waits 30 seconds and performs health check
   - Adds deployment summary with app URL

**Required secrets**:
- `AZURE_CLIENT_ID` - Azure service principal client ID (for OIDC)
- `AZURE_TENANT_ID` - Azure tenant ID
- `AZURE_SUBSCRIPTION_ID` - Azure subscription ID
- `AZURE_RESOURCE_GROUP` - Resource group name
- `GRAPH_TENANT_ID` - Microsoft Graph tenant ID
- `GRAPH_CLIENT_ID` - Graph API client ID
- `GRAPH_CLIENT_SECRET` - Graph API client secret
- `GRAPH_USER_ID` - Graph user ID to query
- `API_TOKEN` - API authentication token

### 4. Security Scan (`security.yml`)
**Triggers**:
- Weekly on Sunday at midnight UTC (scheduled)
- Pull requests to `main`
- Pushes to `main`
- Manual workflow dispatch

**What it does**:
- Runs dependency review on pull requests
- Scans code with Bandit for security issues
- Checks dependencies with Safety for vulnerabilities
- Uploads results to GitHub Security tab (SARIF format)
- Adds security summary to PR

**Required secrets**: None

## Setup Instructions

### 1. Configure Azure OIDC (Recommended)

Create Azure service principal with federated credentials:

```bash
# Create service principal
az ad sp create-for-rbac --name "eventkit-agent-github" \
  --role contributor \
  --scopes /subscriptions/{subscription-id}/resourceGroups/{resource-group}

# Add federated credential for main branch
az ad app federated-credential create \
  --id {app-id} \
  --parameters '{
    "name": "github-main",
    "issuer": "https://token.actions.githubusercontent.com",
    "subject": "repo:{org}/{repo}:ref:refs/heads/main",
    "audiences": ["api://AzureADTokenExchange"]
  }'

# Add federated credential for environment (optional)
az ad app federated-credential create \
  --id {app-id} \
  --parameters '{
    "name": "github-prod",
    "issuer": "https://token.actions.githubusercontent.com",
    "subject": "repo:{org}/{repo}:environment:prod",
    "audiences": ["api://AzureADTokenExchange"]
  }'
```

### 2. Add GitHub Secrets

Go to repository Settings → Secrets and variables → Actions:

**Azure Deployment** (required):
```
AZURE_CLIENT_ID=<client-id-from-sp>
AZURE_TENANT_ID=<tenant-id>
AZURE_SUBSCRIPTION_ID=<subscription-id>
AZURE_RESOURCE_GROUP=eventkit-agent-rg
```

**Application Secrets** (required):
```
GRAPH_TENANT_ID=<your-tenant-id>
GRAPH_CLIENT_ID=<your-client-id>
GRAPH_CLIENT_SECRET=<your-client-secret>
GRAPH_USER_ID=<user-id-to-query>
API_TOKEN=<random-secure-token>
```

**Optional**:
```
CODECOV_TOKEN=<codecov-upload-token>
```

### 3. Create Azure Resource Group

```bash
az group create --name eventkit-agent-rg --location eastus
```

### 4. Configure GitHub Environments (Optional)

For additional control, create environments in GitHub:

1. Go to Settings → Environments
2. Create environments: `dev`, `staging`, `prod`
3. Add protection rules:
   - **prod**: Require approvals before deployment
   - Add environment-specific secrets if needed

### 5. Test the Pipeline

```bash
# Test locally first
make test
make lint

# Push to feature branch (runs tests + lint)
git checkout -b feature/test-ci
git push origin feature/test-ci

# Open PR (runs all checks)

# Merge to main (triggers deployment)
```

## Manual Deployment

You can manually trigger deployment:

1. Go to Actions → Deploy to Azure
2. Click "Run workflow"
3. Select environment (dev/staging/prod)
4. Click "Run workflow"

## Monitoring Deployments

### View Workflow Runs
- Go to Actions tab in GitHub
- Click on specific workflow run
- View logs and summaries

### Check Deployment Status
After deployment completes:
```bash
# Get app URL from workflow output
curl https://{app-name}.azurewebsites.net/health
```

### View Azure Resources
```bash
# List resources in group
az resource list --resource-group eventkit-agent-rg --output table

# Get app service URL
az webapp show \
  --name {app-name} \
  --resource-group eventkit-agent-rg \
  --query defaultHostName \
  --output tsv
```

## Troubleshooting

### Build Failures

**Issue**: Docker build fails
- Check Dockerfile syntax
- Verify all files are included in context
- Review build logs for missing dependencies

**Issue**: Tests fail in CI but pass locally
- Check Python version (CI uses 3.11)
- Verify all dependencies in requirements.txt
- Check for environment-specific issues

### Deployment Failures

**Issue**: Azure login fails
- Verify OIDC federated credentials are configured
- Check that service principal has correct permissions
- Ensure subscription ID is correct

**Issue**: Bicep deployment fails
- Validate Bicep template: `az bicep build --file infra/main.bicep`
- Check parameter values in .bicepparam files
- Review deployment logs in Azure Portal

**Issue**: Health check fails after deployment
- Check app logs: `az webapp log tail --name {app-name} --resource-group {rg}`
- Verify all secrets are configured in Key Vault
- Check container is running: `az webapp show --name {app-name} --resource-group {rg}`

### Security Scan Failures

**Issue**: Bandit reports security issues
- Review the specific issues reported
- Update .bandit config to skip false positives
- Fix legitimate security concerns

**Issue**: Safety reports vulnerabilities
- Update dependencies: `pip list --outdated`
- Check for security patches
- Update requirements.txt with fixed versions

## Best Practices

1. **Never commit secrets** - Use GitHub Secrets and Azure Key Vault
2. **Test locally first** - Run `make test` and `make lint` before pushing
3. **Use feature branches** - Create PRs for all changes
4. **Monitor deployments** - Check health endpoint after deploy
5. **Review security scans** - Address vulnerabilities promptly
6. **Use semantic versioning** - Tag releases with version numbers
7. **Document changes** - Update CHANGELOG.md for releases

## CI/CD Pipeline Architecture

```
┌─────────────┐
│  Developer  │
└──────┬──────┘
       │ git push
       ▼
┌─────────────────┐
│ GitHub Actions  │
├─────────────────┤
│ 1. Run Tests    │ ◄── test.yml
│ 2. Run Lint     │ ◄── lint.yml
│ 3. Security     │ ◄── security.yml
└──────┬──────────┘
       │ on merge to main
       ▼
┌─────────────────┐
│ Build & Deploy  │ ◄── deploy.yml
├─────────────────┤
│ 1. Build Docker │
│ 2. Push to GHCR │
│ 3. Deploy Bicep │
│ 4. Health Check │
└──────┬──────────┘
       │
       ▼
┌─────────────────┐
│ Azure App Svc   │
├─────────────────┤
│ • Web App       │
│ • Key Vault     │
│ • App Insights  │
│ • Storage       │
└─────────────────┘
```

## Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Azure Bicep Documentation](https://learn.microsoft.com/azure/azure-resource-manager/bicep/)
- [OIDC with Azure](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-azure)
