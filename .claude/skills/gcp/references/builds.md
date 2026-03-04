# gcloud builds — Cloud Build Reference

## Contents
- [Overview](#overview)
- [Submit builds](#submit-builds)
- [Build configuration (cloudbuild.yaml)](#build-configuration-cloudbuildyaml)
- [Build triggers](#build-triggers)
- [Manage builds](#manage-builds)
- [Worker pools](#worker-pools)
- [Common cloud builders](#common-cloud-builders)
- [Troubleshooting](#troubleshooting)

## Overview

Cloud Build is a serverless CI/CD platform that executes build steps defined in `cloudbuild.yaml` (or Dockerfile). It can build container images, run tests, and deploy to GCP services.

## Submit builds

```bash
# Build from current directory using Dockerfile
gcloud builds submit --tag=IMAGE_URL .
gcloud builds submit --tag=gcr.io/PROJECT/IMAGE:TAG .
gcloud builds submit --tag=REGION-docker.pkg.dev/PROJECT/REPO/IMAGE:TAG .

# Build using a cloudbuild.yaml
gcloud builds submit --config=cloudbuild.yaml .

# Build from GCS source
gcloud builds submit --tag=IMAGE_URL gs://BUCKET/source.tar.gz

# Build with substitution variables
gcloud builds submit --config=cloudbuild.yaml \
  --substitutions=_ENV=prod,_VERSION=1.2.3 .

# Specify machine type for faster builds
gcloud builds submit --config=cloudbuild.yaml \
  --machine-type=e2-highcpu-32 .

# Use a specific service account
gcloud builds submit --config=cloudbuild.yaml \
  --service-account=projects/PROJECT/serviceAccounts/SA_EMAIL .

# Suppress logs
gcloud builds submit --tag=IMAGE_URL . --suppress-logs
```

## Build configuration (cloudbuild.yaml)

```yaml
steps:
  # Build container
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', '${_IMAGE_URL}', '.']

  # Run tests
  - name: 'gcr.io/cloud-builders/docker'
    args: ['run', '${_IMAGE_URL}', 'pytest']

  # Deploy to Cloud Run
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    args: ['gcloud', 'run', 'deploy', 'my-service',
           '--image', '${_IMAGE_URL}',
           '--region', 'us-central1']

images:
  - '${_IMAGE_URL}'

substitutions:
  _IMAGE_URL: 'gcr.io/${PROJECT_ID}/my-app:${SHORT_SHA}'

options:
  machineType: 'E2_HIGHCPU_8'
  logging: CLOUD_LOGGING_ONLY
```

### Built-in substitutions

| Variable | Description |
|----------|-------------|
| `$PROJECT_ID` | Build project ID |
| `$BUILD_ID` | Unique build ID |
| `$COMMIT_SHA` | Full commit SHA |
| `$SHORT_SHA` | First 7 chars of commit SHA |
| `$REPO_NAME` | Repository name |
| `$BRANCH_NAME` | Branch name |
| `$TAG_NAME` | Tag name |
| `$REVISION_ID` | Same as COMMIT_SHA |

## Build triggers

```bash
# Create trigger from GitHub repo
gcloud builds triggers create github \
  --name=TRIGGER_NAME \
  --repo-name=REPO \
  --repo-owner=OWNER \
  --branch-pattern="^main$" \
  --build-config=cloudbuild.yaml

# Create trigger from Cloud Source Repositories
gcloud builds triggers create cloud-source-repositories \
  --name=TRIGGER_NAME \
  --repo=REPO \
  --branch-pattern="^main$" \
  --build-config=cloudbuild.yaml

# Trigger on tag push
gcloud builds triggers create github \
  --name=release-trigger \
  --repo-name=REPO --repo-owner=OWNER \
  --tag-pattern="^v[0-9]+\\..*" \
  --build-config=cloudbuild.yaml

# List triggers
gcloud builds triggers list

# Describe
gcloud builds triggers describe TRIGGER_NAME

# Run a trigger manually
gcloud builds triggers run TRIGGER_NAME --branch=main

# Delete
gcloud builds triggers delete TRIGGER_NAME
```

## Manage builds

```bash
# List recent builds
gcloud builds list --limit=10

# Describe a build
gcloud builds describe BUILD_ID

# View build logs
gcloud builds log BUILD_ID

# Stream logs of a running build
gcloud builds log --stream BUILD_ID

# Cancel a build
gcloud builds cancel BUILD_ID
```

## Worker pools

```bash
# Create a private worker pool
gcloud builds worker-pools create POOL_NAME \
  --region=REGION \
  --worker-machine-type=e2-standard-4 \
  --worker-disk-size=100GB

# Use in cloudbuild.yaml
# options:
#   pool:
#     name: 'projects/PROJECT/locations/REGION/workerPools/POOL_NAME'

# List pools
gcloud builds worker-pools list --region=REGION

# Delete
gcloud builds worker-pools delete POOL_NAME --region=REGION
```

## Common cloud builders

| Builder | Purpose |
|---------|---------|
| `gcr.io/cloud-builders/docker` | Docker build, push, run |
| `gcr.io/cloud-builders/gcloud` | Run gcloud commands |
| `gcr.io/cloud-builders/kubectl` | Kubernetes deployments |
| `gcr.io/cloud-builders/npm` | Node.js builds |
| `gcr.io/cloud-builders/go` | Go builds |
| `gcr.io/cloud-builders/git` | Git operations |
| `gcr.io/google.com/cloudsdktool/cloud-sdk` | Full gcloud SDK |

## Troubleshooting

- **"Access denied"** — Cloud Build service account (`PROJECT_NUMBER@cloudbuild.gserviceaccount.com`) needs appropriate roles
- **Build timeout** — default is 10 minutes; increase with `timeout: '1200s'` in cloudbuild.yaml or `--timeout=1200s`
- **Large context** — use `.gcloudignore` to exclude unnecessary files from upload
- **View logs** — `gcloud builds log BUILD_ID` or check Cloud Console
- **Substitution errors** — user-defined substitutions must start with `_` (underscore)
