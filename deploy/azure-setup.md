# Azure Deployment Setup

One-time setup to provision all Azure resources and configure GitHub Actions secrets.
Run these commands from your terminal with the Azure CLI installed (`az login` first).

---

## Prerequisites

```bash
az login
az extension add --name containerapp --upgrade -y
```

---

## Step 1 — Set your variables

```bash
SUBSCRIPTION_ID="<your-azure-subscription-id>"
RESOURCE_GROUP="source-club-rg"
LOCATION="eastus"                      # or your preferred region
ACR_NAME="inflexisacr"                 # must be globally unique, lowercase, no hyphens
CONTAINER_ENV="source-club-env"
CONTAINER_APP="source-club-app"
```

---

## Step 2 — Create resource group

```bash
az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION
```

---

## Step 3 — Create Azure Container Registry (ACR)

```bash
az acr create \
  --resource-group $RESOURCE_GROUP \
  --name $ACR_NAME \
  --sku Basic \
  --admin-enabled true
```

Get the login server (you'll need this for GitHub secrets):
```bash
az acr show --name $ACR_NAME --query loginServer -o tsv
# → inflexisacr.azurecr.io
```

---

## Step 4 — Create Container Apps environment

```bash
az containerapp env create \
  --name $CONTAINER_ENV \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION
```

---

## Step 5 — Initial deploy (first time, before GitHub Actions takes over)

```bash
# Build and push the image manually for the first deploy
az acr build \
  --registry $ACR_NAME \
  --image source-club-casestudy:latest \
  .

# Create the container app
az containerapp create \
  --name $CONTAINER_APP \
  --resource-group $RESOURCE_GROUP \
  --environment $CONTAINER_ENV \
  --image $ACR_NAME.azurecr.io/source-club-casestudy:latest \
  --registry-server $ACR_NAME.azurecr.io \
  --registry-identity system \
  --target-port 8501 \
  --ingress external \
  --min-replicas 1 \
  --max-replicas 3 \
  --cpu 0.5 \
  --memory 1.0Gi \
  --secrets anthropic-api-key=<YOUR_ANTHROPIC_API_KEY> \
  --env-vars ANTHROPIC_API_KEY=secretref:anthropic-api-key
```

Get the public URL:
```bash
az containerapp show \
  --name $CONTAINER_APP \
  --resource-group $RESOURCE_GROUP \
  --query properties.configuration.ingress.fqdn -o tsv
# → source-club-app.nicename.eastus.azurecontainerapps.io
```

---

## Step 6 — Add GitHub Actions secrets

In your GitHub repo → **Settings → Secrets and variables → Actions → New repository secret**:

| Secret name | Value |
|-------------|-------|
| `AZURE_CREDENTIALS` | Output of the command below |
| `ACR_LOGIN_SERVER` | `inflexisacr.azurecr.io` (from Step 3) |
| `ACR_NAME` | `inflexisacr` |
| `AZURE_RESOURCE_GROUP` | `source-club-rg` |

Generate the `AZURE_CREDENTIALS` JSON:
```bash
az ad sp create-for-rbac \
  --name "source-club-github-actions" \
  --role contributor \
  --scopes /subscriptions/$SUBSCRIPTION_ID/resourceGroups/$RESOURCE_GROUP \
  --json-auth
```

Copy the entire JSON output as the value for `AZURE_CREDENTIALS`.

---

## After Setup

Every push to `main` automatically:
1. Builds a new Docker image
2. Pushes it to ACR
3. Updates the Container App with the new image (zero-downtime rolling deploy)

Manual trigger: GitHub → Actions → **Build & Deploy to Azure Container Apps** → **Run workflow**

---

## Cost Estimate

| Resource | Tier | Est. Monthly Cost |
|----------|------|------------------|
| Azure Container Registry | Basic | ~$5/mo |
| Azure Container Apps | Consumption (0.5 vCPU / 1GB) | ~$5–15/mo depending on traffic |
| **Total** | | **~$10–20/mo** |

Free tier note: Azure Container Apps has a generous free grant (180,000 vCPU-seconds/month). For demo traffic, this is likely **free or near-free**.
