# Azure Deployment with Microsoft Entra ID Authentication

This bonus track package allows Northwind Furnishings fit-out engine to be deployed to **Azure Container Apps** with enterprise-grade **Microsoft Entra ID (Azure AD)** authentication.

---

## 1. Prerequisites

- Azure CLI (`az`) installed and authenticated (`az login`)
- An Azure subscription and resource group
- A registered Microsoft Entra ID Application (App Registration)

---

## 2. Infrastructure Deployment (Azure Bicep)

Deploy the container environment and container app:

```bash
az deployment group create \
  --resource-group rg-rulebound \
  --template-file azure/main.bicep \
  --parameters appName=northwind-fitout-engine \
               entraClientId=<your-app-client-id> \
               entraTenantId=<your-tenant-id>
```

---

## 3. Authenticating with Microsoft Entra ID

Acquire a bearer token using Azure CLI:

```bash
# Acquire OAuth2 Bearer token for your registered API scope
TOKEN=$(az account get-access-token --resource api://<your-app-client-id> --query accessToken -o tsv)
```

---

## 4. Invoking the Authenticated API

### Health Check (Public):
```bash
curl -i https://<app-fqdn>/health
```

### Run Authenticated Layout & Quote Generation:
```bash
curl -i -X POST https://<app-fqdn>/api/v1/quote/ROOM-01 \
  -H "Authorization: Bearer $TOKEN"
```

The response returns:
1. `layout`: Validated layout with zero spatial violations.
2. `quote`: Reconciled quote with line-level arithmetic traces.
3. `authenticated_user`: Verified Entra ID principal identity.
