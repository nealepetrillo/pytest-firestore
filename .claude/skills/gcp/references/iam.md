# gcloud iam — Identity, Access Management & Service Accounts Reference

## Contents
- [Service Accounts](#service-accounts)
- [IAM Policies — Project Level](#iam-policies--project-level)
- [IAM Policies — Resource Level](#iam-policies--resource-level)
- [Roles](#roles)
- [Workload Identity Federation](#workload-identity-federation)
- [Workload Identity for GKE](#workload-identity-for-gke)
- [Troubleshooting](#troubleshooting)

## Service Accounts

Service accounts are non-human identities used by applications, VMs, and CI/CD pipelines to authenticate to GCP APIs.

### Create and manage

```bash
# Create a service account
gcloud iam service-accounts create SA_NAME \
  --display-name="Human-readable description" \
  --description="Longer description of purpose"

# List service accounts
gcloud iam service-accounts list
gcloud iam service-accounts list --format="table(email,displayName,disabled)"

# Describe a service account
gcloud iam service-accounts describe SA_EMAIL

# Update display name or description
gcloud iam service-accounts update SA_EMAIL \
  --display-name="New Display Name"

# Disable / enable
gcloud iam service-accounts disable SA_EMAIL
gcloud iam service-accounts enable SA_EMAIL

# Delete
gcloud iam service-accounts delete SA_EMAIL

# Undelete (within 30 days)
gcloud iam service-accounts undelete SA_UNIQUE_ID
```

SA email format: `SA_NAME@PROJECT_ID.iam.gserviceaccount.com`

### Key management

Prefer Workload Identity or impersonation over key files when possible.

```bash
# Create a JSON key file
gcloud iam service-accounts keys create KEY_FILE.json \
  --iam-account=SA_EMAIL

# List keys
gcloud iam service-accounts keys list --iam-account=SA_EMAIL

# Delete a key
gcloud iam service-accounts keys delete KEY_ID --iam-account=SA_EMAIL

# Upload a public key (for externally managed keys)
gcloud iam service-accounts keys upload PUBLIC_KEY_FILE \
  --iam-account=SA_EMAIL
```

### Impersonation

Use impersonation instead of downloading keys:

```bash
# Per-command
gcloud COMMAND --impersonate-service-account=SA_EMAIL

# Set as default
gcloud config set auth/impersonate_service_account SA_EMAIL

# Generate an access token as the SA
gcloud auth print-access-token --impersonate-service-account=SA_EMAIL

# Generate an identity token as the SA
gcloud auth print-identity-token --impersonate-service-account=SA_EMAIL \
  --audiences=https://my-service.run.app
```

Requirement: caller needs `roles/iam.serviceAccountTokenCreator` on the target SA.

## IAM Policies — Project Level

### View policy

```bash
gcloud projects get-iam-policy PROJECT_ID
gcloud projects get-iam-policy PROJECT_ID --format=json
gcloud projects get-iam-policy PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.role:roles/editor" \
  --format="table(bindings.members)"
```

### Grant a role

```bash
# To a user
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="user:email@example.com" \
  --role="roles/ROLE_NAME"

# To a service account
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:SA_EMAIL" \
  --role="roles/ROLE_NAME"

# To a group
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="group:group@example.com" \
  --role="roles/ROLE_NAME"

# With a condition
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="user:email@example.com" \
  --role="roles/ROLE_NAME" \
  --condition='expression=request.time < timestamp("2025-12-31T00:00:00Z"),title=expires_2025,description=Temporary access'
```

### Remove a role

```bash
gcloud projects remove-iam-policy-binding PROJECT_ID \
  --member="user:email@example.com" \
  --role="roles/ROLE_NAME"
```

### Set entire policy from file

```bash
gcloud projects get-iam-policy PROJECT_ID --format=json > policy.json
# Edit policy.json
gcloud projects set-iam-policy PROJECT_ID policy.json
```

## IAM Policies — Resource Level

Many resources support resource-level IAM bindings:

```bash
# Cloud Run service
gcloud run services add-iam-policy-binding SERVICE \
  --member="allUsers" --role="roles/run.invoker" --region=REGION

# Cloud Function
gcloud functions add-iam-policy-binding FUNCTION \
  --member="serviceAccount:SA_EMAIL" --role="roles/cloudfunctions.invoker" \
  --region=REGION

# Pub/Sub topic
gcloud pubsub topics add-iam-policy-binding TOPIC \
  --member="serviceAccount:SA_EMAIL" --role="roles/pubsub.publisher"

# Storage bucket
gcloud storage buckets add-iam-policy-binding gs://BUCKET \
  --member="serviceAccount:SA_EMAIL" --role="roles/storage.objectViewer"

# Service account (grant others permission to use it)
gcloud iam service-accounts add-iam-policy-binding SA_EMAIL \
  --member="user:dev@example.com" --role="roles/iam.serviceAccountUser"
```

## Roles

### Predefined roles — common ones

| Role | Description |
|------|-------------|
| `roles/viewer` | Read-only access to all resources |
| `roles/editor` | Read-write access (no IAM changes) |
| `roles/owner` | Full access including IAM and billing |
| `roles/iam.serviceAccountUser` | Can run operations as a service account |
| `roles/iam.serviceAccountTokenCreator` | Can create tokens / impersonate SA |
| `roles/iam.serviceAccountAdmin` | Full control over service accounts |
| `roles/iam.workloadIdentityUser` | Bind Kubernetes SA to GCP SA |
| `roles/run.invoker` | Can invoke Cloud Run services |
| `roles/run.admin` | Full Cloud Run management |
| `roles/cloudfunctions.invoker` | Can invoke Cloud Functions |
| `roles/cloudfunctions.developer` | Deploy and manage functions |
| `roles/storage.objectViewer` | Read GCS objects |
| `roles/storage.objectAdmin` | Read/write/delete GCS objects |
| `roles/pubsub.publisher` | Publish to Pub/Sub topics |
| `roles/pubsub.subscriber` | Pull from Pub/Sub subscriptions |
| `roles/secretmanager.secretAccessor` | Read secret versions |
| `roles/logging.logWriter` | Write log entries |
| `roles/monitoring.metricWriter` | Write monitoring metrics |

### List and search roles

```bash
# List all predefined roles
gcloud iam roles list

# Search for roles by keyword
gcloud iam roles list --filter="name:storage"

# Describe a role (see permissions)
gcloud iam roles describe roles/storage.objectAdmin

# List custom roles in project
gcloud iam roles list --project=PROJECT_ID
```

### Custom roles

```bash
# Create from a YAML file
gcloud iam roles create ROLE_ID --project=PROJECT_ID --file=role.yaml

# Create inline
gcloud iam roles create ROLE_ID --project=PROJECT_ID \
  --title="Custom Role Title" \
  --description="What this role does" \
  --permissions=storage.objects.get,storage.objects.list \
  --stage=GA

# Update
gcloud iam roles update ROLE_ID --project=PROJECT_ID \
  --add-permissions=storage.objects.create

# Delete / undelete
gcloud iam roles delete ROLE_ID --project=PROJECT_ID
gcloud iam roles undelete ROLE_ID --project=PROJECT_ID
```

## Workload Identity Federation

Authenticate external workloads (GitHub Actions, AWS, Azure, on-prem) without key files.

```bash
# Create a workload identity pool
gcloud iam workload-identity-pools create POOL_ID \
  --location=global \
  --display-name="Pool Display Name"

# Create a provider (e.g. GitHub Actions)
gcloud iam workload-identity-pools providers create-oidc PROVIDER_ID \
  --location=global \
  --workload-identity-pool=POOL_ID \
  --display-name="GitHub Actions" \
  --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository" \
  --issuer-uri="https://token.actions.githubusercontent.com"

# Bind an SA to the external identity
gcloud iam service-accounts add-iam-policy-binding SA_EMAIL \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/PROJECT_NUM/locations/global/workloadIdentityPools/POOL_ID/attribute.repository/ORG/REPO"
```

## Workload Identity for GKE

Bind Kubernetes service accounts to GCP service accounts:

```bash
# Enable on cluster
gcloud container clusters update CLUSTER \
  --workload-pool=PROJECT_ID.svc.id.goog --region=REGION

# Bind KSA to GSA
gcloud iam service-accounts add-iam-policy-binding GSA_EMAIL \
  --role="roles/iam.workloadIdentityUser" \
  --member="serviceAccount:PROJECT_ID.svc.id.goog[K8S_NAMESPACE/KSA_NAME]"

# Annotate the Kubernetes SA
kubectl annotate serviceaccount KSA_NAME \
  --namespace=K8S_NAMESPACE \
  iam.gke.io/gcp-service-account=GSA_EMAIL
```

## Troubleshooting

- **"Permission denied"** — use `gcloud projects get-iam-policy` to check bindings; use `--flatten` and `--filter` to find specific members
- **"Service account does not exist"** — check email format: `NAME@PROJECT.iam.gserviceaccount.com`
- **Key file issues** — verify `GOOGLE_APPLICATION_CREDENTIALS` points to valid JSON; check key hasn't been deleted with `keys list`
- **Impersonation errors** — caller needs `roles/iam.serviceAccountTokenCreator` on the target SA
- **Audit who has access** — `gcloud asset search-all-iam-policies --query="policy:MEMBER_EMAIL"` (requires Cloud Asset API)
- **Test permissions** — `gcloud projects test-iam-permissions PROJECT_ID --permissions=PERMISSION1,PERMISSION2`
