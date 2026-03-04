# gcloud secrets — Secret Manager Reference

## Contents
- [Overview](#overview)
- [Secrets](#secrets)
- [Versions](#versions)
- [IAM](#iam)
- [Integration with other services](#integration-with-other-services)
- [Notifications](#notifications)
- [Common patterns](#common-patterns)
- [Troubleshooting](#troubleshooting)

## Overview

Secret Manager stores API keys, passwords, certificates, and other sensitive data. Secrets have versions, and access is controlled via IAM. Secrets are encrypted at rest and in transit.

## Secrets

### Create and manage

```bash
# Create a secret
gcloud secrets create SECRET_NAME --replication-policy=automatic

# Create with specific replication
gcloud secrets create SECRET_NAME \
  --replication-policy=user-managed \
  --locations=us-central1,us-east1

# Create and add a version in one step
echo -n "my-secret-value" | gcloud secrets create SECRET_NAME --data-file=-

# Create from a file
gcloud secrets create SECRET_NAME --data-file=./secret.txt

# List secrets
gcloud secrets list
gcloud secrets list --format="table(name,replication.automatic,createTime)"

# Describe
gcloud secrets describe SECRET_NAME

# Update labels
gcloud secrets update SECRET_NAME --update-labels=env=prod,app=api

# Set expiration
gcloud secrets update SECRET_NAME --expire-time="2026-12-31T00:00:00Z"
gcloud secrets update SECRET_NAME --ttl=90d

# Delete
gcloud secrets delete SECRET_NAME
```

## Versions

```bash
# Add a new version
echo -n "new-secret-value" | gcloud secrets versions add SECRET_NAME --data-file=-

# Add from file
gcloud secrets versions add SECRET_NAME --data-file=./new-secret.txt

# Access (read) the latest version
gcloud secrets versions access latest --secret=SECRET_NAME

# Access a specific version
gcloud secrets versions access 3 --secret=SECRET_NAME

# List versions
gcloud secrets versions list SECRET_NAME

# Describe a version
gcloud secrets versions describe VERSION_ID --secret=SECRET_NAME

# Disable a version (cannot be accessed until re-enabled)
gcloud secrets versions disable VERSION_ID --secret=SECRET_NAME

# Enable
gcloud secrets versions enable VERSION_ID --secret=SECRET_NAME

# Destroy a version (permanent, cannot be undone)
gcloud secrets versions destroy VERSION_ID --secret=SECRET_NAME
```

## IAM

```bash
# Grant access to read secrets
gcloud secrets add-iam-policy-binding SECRET_NAME \
  --member="serviceAccount:SA_EMAIL" \
  --role="roles/secretmanager.secretAccessor"

# Grant access to manage secrets
gcloud secrets add-iam-policy-binding SECRET_NAME \
  --member="user:email@example.com" \
  --role="roles/secretmanager.admin"

# View IAM policy
gcloud secrets get-iam-policy SECRET_NAME

# Remove access
gcloud secrets remove-iam-policy-binding SECRET_NAME \
  --member="serviceAccount:SA_EMAIL" \
  --role="roles/secretmanager.secretAccessor"
```

### Common roles

| Role | Description |
|------|-------------|
| `roles/secretmanager.secretAccessor` | Read secret values |
| `roles/secretmanager.secretVersionAdder` | Add new versions |
| `roles/secretmanager.secretVersionManager` | Manage versions (disable, enable, destroy) |
| `roles/secretmanager.admin` | Full management |
| `roles/secretmanager.viewer` | View metadata (not values) |

## Integration with other services

### Cloud Functions

```bash
gcloud functions deploy FUNCTION_NAME \
  --set-secrets=ENV_VAR=SECRET_NAME:latest
# Or mount as a file:
gcloud functions deploy FUNCTION_NAME \
  --set-secrets=/path/to/secret=SECRET_NAME:latest
```

### Cloud Run

```bash
gcloud run deploy SERVICE_NAME \
  --set-secrets=ENV_VAR=SECRET_NAME:latest
# Or as a volume mount:
gcloud run deploy SERVICE_NAME \
  --set-secrets=/secrets/my-secret=SECRET_NAME:latest
```

## Notifications

```bash
# Add a Pub/Sub topic for secret events
gcloud secrets update SECRET_NAME \
  --add-topics=projects/PROJECT/topics/TOPIC_NAME

# Remove
gcloud secrets update SECRET_NAME \
  --remove-topics=projects/PROJECT/topics/TOPIC_NAME
```

## Common patterns

### Rotate a secret

```bash
# Add new version
echo -n "new-password" | gcloud secrets versions add SECRET_NAME --data-file=-

# Verify new version works, then disable old
gcloud secrets versions disable OLD_VERSION --secret=SECRET_NAME
```

### Access in application code (Python)

```python
from google.cloud import secretmanager

client = secretmanager.SecretManagerServiceClient()
name = f"projects/PROJECT_ID/secrets/SECRET_NAME/versions/latest"
response = client.access_secret_version(request={"name": name})
secret_value = response.payload.data.decode("UTF-8")
```

## Troubleshooting

- **"Permission denied"** — ensure caller has `roles/secretmanager.secretAccessor` on the specific secret
- **"Secret version is disabled"** — re-enable with `gcloud secrets versions enable`
- **"Secret version is destroyed"** — destroyed versions cannot be recovered; add a new version
- **Cost management** — you are billed per secret version and access operation; destroy unused versions
- **Rotation** — Secret Manager supports automatic rotation via Pub/Sub notifications and Cloud Functions
