# gcloud storage — Cloud Storage Reference

## Contents
- [Overview](#overview)
- [Buckets](#buckets)
- [Objects](#objects)
  - [Signed URLs (CLI)](#signed-urls)
  - [Signed URLs in Python (without a key file)](#signed-urls-in-python-without-a-key-file)
- [IAM and access control](#iam-and-access-control)
- [Notifications (Pub/Sub)](#notifications-pubsub)
- [gsutil (legacy CLI)](#gsutil-legacy-cli)
- [Common patterns](#common-patterns)
- [Troubleshooting](#troubleshooting)

## Overview

Cloud Storage provides object storage for unstructured data. The `gcloud storage` command group (replacing legacy `gsutil`) manages buckets and objects. Bucket names are globally unique.

## Buckets

### Create

```bash
gcloud storage buckets create gs://BUCKET_NAME \
  --location=LOCATION \
  --default-storage-class=STANDARD

# With uniform bucket-level access (recommended)
gcloud storage buckets create gs://BUCKET_NAME \
  --location=US \
  --uniform-bucket-level-access

# Regional bucket
gcloud storage buckets create gs://BUCKET_NAME \
  --location=us-central1

# Dual-region
gcloud storage buckets create gs://BUCKET_NAME \
  --location=US \
  --placement=us-central1,us-east1
```

**Storage classes:** `STANDARD`, `NEARLINE` (30-day min), `COLDLINE` (90-day min), `ARCHIVE` (365-day min)

### Manage buckets

```bash
# List buckets
gcloud storage buckets list
gcloud storage buckets list --format="table(name,location,storageClass)"

# Describe
gcloud storage buckets describe gs://BUCKET_NAME

# Update settings
gcloud storage buckets update gs://BUCKET_NAME \
  --default-storage-class=NEARLINE

# Enable versioning
gcloud storage buckets update gs://BUCKET_NAME --versioning

# Disable versioning
gcloud storage buckets update gs://BUCKET_NAME --no-versioning

# Set lifecycle rules (from JSON file)
gcloud storage buckets update gs://BUCKET_NAME \
  --lifecycle-file=lifecycle.json

# Delete (must be empty)
gcloud storage buckets delete gs://BUCKET_NAME

# Delete bucket and all contents
gcloud storage rm --recursive gs://BUCKET_NAME
```

## Objects

### Upload and download

```bash
# Upload a file
gcloud storage cp LOCAL_FILE gs://BUCKET/PATH

# Upload a directory
gcloud storage cp --recursive LOCAL_DIR gs://BUCKET/PATH

# Download a file
gcloud storage cp gs://BUCKET/PATH LOCAL_FILE

# Download a directory
gcloud storage cp --recursive gs://BUCKET/PATH LOCAL_DIR

# Copy between buckets
gcloud storage cp gs://SRC_BUCKET/FILE gs://DST_BUCKET/FILE

# Sync a directory (upload only changed files)
gcloud storage rsync LOCAL_DIR gs://BUCKET/PATH
gcloud storage rsync --recursive --delete-unmatched-destination-objects \
  LOCAL_DIR gs://BUCKET/PATH
```

### List and manage objects

```bash
# List objects
gcloud storage ls gs://BUCKET
gcloud storage ls gs://BUCKET/PREFIX/
gcloud storage ls --recursive gs://BUCKET
gcloud storage ls --long gs://BUCKET    # Includes size and date

# Get object metadata
gcloud storage objects describe gs://BUCKET/OBJECT

# Move / rename
gcloud storage mv gs://BUCKET/OLD_NAME gs://BUCKET/NEW_NAME

# Delete objects
gcloud storage rm gs://BUCKET/OBJECT
gcloud storage rm --recursive gs://BUCKET/PREFIX/

# Set metadata
gcloud storage objects update gs://BUCKET/OBJECT \
  --content-type=application/json \
  --custom-metadata=key=value
```

### Signed URLs

```bash
# Generate a signed URL (requires service account key or impersonation)
gcloud storage sign-url gs://BUCKET/OBJECT \
  --duration=1h \
  --private-key-file=KEY.json

# Using impersonation (no key file needed)
gcloud storage sign-url gs://BUCKET/OBJECT \
  --duration=1h \
  --impersonate-service-account=SA_EMAIL
```

### Signed URLs in Python (without a key file)

On Cloud Run, Cloud Functions, GKE, or any environment using Application Default Credentials (ADC), you typically don't have a service account key file. The standard `blob.generate_signed_url()` call will fail without one. The workaround is to **refresh the default credentials** to obtain an access token, then pass both the service account email and the token to `generate_signed_url()`.

**Required imports:**
```python
import google.auth
import google.auth.credentials
import google.auth.transport.requests
from google.cloud import storage
```

**Step 1 — Obtain default credentials (once, at startup):**
```python
credentials, project = google.auth.default()
storage_client = storage.Client()
```

**Step 2 — Refresh credentials and generate signed URL (per request):**
```python
import datetime

# Refresh the access token — required before each signing operation
# because tokens expire (typically after ~1 hour).
credentials.refresh(google.auth.transport.requests.Request())

bucket = storage_client.bucket("my-bucket")
blob = bucket.blob("path/to/object.ext")

signed_url = blob.generate_signed_url(
    version="v4",
    expiration=datetime.timedelta(hours=1),  # URL valid for 1 hour
    method="GET",
    # These two parameters let you sign without a key file:
    service_account_email=credentials.service_account_email,
    access_token=credentials.token,
)
```

**Optional parameters for `generate_signed_url()`:**
```python
signed_url = blob.generate_signed_url(
    version="v4",
    expiration=datetime.timedelta(days=7),
    method="GET",
    service_account_email=credentials.service_account_email,
    access_token=credentials.token,
    # Force download with a specific filename:
    response_disposition=f"attachment; filename={filename}",
    # Set content type for inline display:
    response_type="video/mp4",
)
```

**Key points:**
- `credentials.refresh()` must be called before signing — the token may be expired or not yet fetched
- The `service_account_email` and `access_token` parameters together replace the need for a key file
- This works with any ADC-provided credentials that have a `service_account_email` attribute (service accounts on Cloud Run, GKE with Workload Identity, etc.)
- The underlying service account must have the `iam.serviceAccounts.signBlob` permission on itself (granted by `roles/iam.serviceAccountTokenCreator`)
- For upload signed URLs, change `method="PUT"` and optionally set `content_type`

## IAM and access control

```bash
# Get bucket IAM policy
gcloud storage buckets get-iam-policy gs://BUCKET

# Grant access
gcloud storage buckets add-iam-policy-binding gs://BUCKET \
  --member="user:email@example.com" \
  --role="roles/storage.objectViewer"

gcloud storage buckets add-iam-policy-binding gs://BUCKET \
  --member="allUsers" \
  --role="roles/storage.objectViewer"   # Make bucket public

# Remove access
gcloud storage buckets remove-iam-policy-binding gs://BUCKET \
  --member="user:email@example.com" \
  --role="roles/storage.objectViewer"
```

## Notifications (Pub/Sub)

```bash
# Create a notification for object changes
gcloud storage buckets notifications create gs://BUCKET \
  --topic=TOPIC_NAME \
  --event-types=OBJECT_FINALIZE

# List notifications
gcloud storage buckets notifications list gs://BUCKET

# Delete
gcloud storage buckets notifications delete gs://BUCKET --notification-id=ID
```

## gsutil (legacy CLI)

`gsutil` is still available and has feature parity. Common differences:

```bash
# gsutil equivalents
gsutil cp FILE gs://BUCKET/
gsutil ls gs://BUCKET
gsutil rsync -r LOCAL_DIR gs://BUCKET/PATH
gsutil mb gs://BUCKET_NAME            # Make bucket
gsutil rb gs://BUCKET_NAME            # Remove bucket
gsutil acl ch -u user@example.com:R gs://BUCKET/OBJECT  # ACL change
```

## Common patterns

### Host a static website

```bash
gcloud storage buckets create gs://www.example.com --location=US
gcloud storage buckets update gs://www.example.com \
  --web-main-page-suffix=index.html \
  --web-not-found-page=404.html
gcloud storage buckets add-iam-policy-binding gs://www.example.com \
  --member=allUsers --role=roles/storage.objectViewer
gcloud storage cp --recursive ./site/* gs://www.example.com/
```

### Lifecycle policy (lifecycle.json)

```json
{
  "rule": [
    {
      "action": {"type": "Delete"},
      "condition": {"age": 365}
    },
    {
      "action": {"type": "SetStorageClass", "storageClass": "COLDLINE"},
      "condition": {"age": 90}
    }
  ]
}
```

## Troubleshooting

- **"Bucket name already exists"** — bucket names are globally unique; choose a different name
- **"Access denied"** — check IAM bindings with `buckets get-iam-policy`; ensure uniform bucket-level access if using IAM
- **Slow uploads** — use `gcloud storage cp` (parallel by default) or `rsync` for incremental syncs
- **Cost management** — use lifecycle rules to auto-delete or transition old objects to cheaper storage classes
- **CORS issues** — set CORS config with `gcloud storage buckets update gs://BUCKET --cors-file=cors.json`
