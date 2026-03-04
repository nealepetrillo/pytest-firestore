# gcloud services — API Management Reference

## Contents
- [Overview](#overview)
- [Enable APIs](#enable-apis)
- [Disable APIs](#disable-apis)
- [List APIs](#list-apis)
- [Operations](#operations)
- [Commonly needed APIs](#commonly-needed-apis)
- [Common patterns](#common-patterns)
- [Troubleshooting](#troubleshooting)

## Overview

`gcloud services` enables and disables Google Cloud APIs for a project. Most GCP resources require their corresponding API to be enabled before use.

## Enable APIs

```bash
# Enable a single API
gcloud services enable firestore.googleapis.com

# Enable multiple APIs at once
gcloud services enable \
  cloudfunctions.googleapis.com \
  cloudbuild.googleapis.com \
  run.googleapis.com \
  secretmanager.googleapis.com

# Enable with async (don't wait for completion)
gcloud services enable bigquery.googleapis.com --async
```

## Disable APIs

```bash
# Disable an API
gcloud services disable translate.googleapis.com

# Force disable (even if other services depend on it)
gcloud services disable translate.googleapis.com --force
```

Disabling an API may delete associated resources. Use with caution.

## List APIs

```bash
# List enabled APIs
gcloud services list --enabled
gcloud services list --enabled --format="value(config.name)"

# List available (all) APIs
gcloud services list --available

# Filter enabled APIs
gcloud services list --enabled --filter="name:storage"

# Check if a specific API is enabled
gcloud services list --enabled --filter="name:firestore.googleapis.com"
```

## Operations

```bash
# List recent API operations
gcloud services operations list

# Describe an operation
gcloud services operations describe OPERATION_NAME

# Wait for an operation
gcloud services operations wait OPERATION_NAME
```

## Commonly needed APIs

| API | Service Name |
|-----|-------------|
| Compute Engine | `compute.googleapis.com` |
| Cloud Functions | `cloudfunctions.googleapis.com` |
| Cloud Run | `run.googleapis.com` |
| Cloud Build | `cloudbuild.googleapis.com` |
| Cloud Storage | `storage.googleapis.com` |
| Firestore | `firestore.googleapis.com` |
| Pub/Sub | `pubsub.googleapis.com` |
| Cloud SQL Admin | `sqladmin.googleapis.com` |
| Secret Manager | `secretmanager.googleapis.com` |
| Cloud Logging | `logging.googleapis.com` |
| Cloud Monitoring | `monitoring.googleapis.com` |
| Artifact Registry | `artifactregistry.googleapis.com` |
| Cloud DNS | `dns.googleapis.com` |
| Cloud KMS | `cloudkms.googleapis.com` |
| IAM | `iam.googleapis.com` |
| Container (GKE) | `container.googleapis.com` |
| App Engine Admin | `appengine.googleapis.com` |
| BigQuery | `bigquery.googleapis.com` |
| Cloud Scheduler | `cloudscheduler.googleapis.com` |
| Eventarc | `eventarc.googleapis.com` |
| Cloud Tasks | `cloudtasks.googleapis.com` |
| Cloud Asset | `cloudasset.googleapis.com` |
| Service Usage | `serviceusage.googleapis.com` |

## Common patterns

### Enable all APIs for a new project

```bash
gcloud services enable \
  compute.googleapis.com \
  container.googleapis.com \
  cloudfunctions.googleapis.com \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com \
  firestore.googleapis.com \
  pubsub.googleapis.com \
  logging.googleapis.com \
  monitoring.googleapis.com
```

### Check what APIs a deployment needs

If a deployment fails with "API not enabled", look for the API name in the error message and enable it.

## Troubleshooting

- **"API not enabled"** — enable the required API with `gcloud services enable`
- **"Permission denied"** — enabling APIs requires `roles/serviceusage.serviceUsageAdmin` or `roles/owner`
- **Disabling breaks things** — disabling an API may delete resources; re-enabling may not restore them
- **Billing required** — most APIs require a billing account linked to the project
- **API enablement is per-project** — each project must independently enable the APIs it uses
