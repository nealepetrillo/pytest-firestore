# gcloud artifacts — Artifact Registry Reference

## Contents
- [Overview](#overview)
- [Repositories](#repositories)
- [Docker images](#docker-images)
- [Package management](#package-management)
- [Cleanup policies](#cleanup-policies)
- [IAM](#iam)
- [Troubleshooting](#troubleshooting)

## Overview

Artifact Registry is Google Cloud's package manager for container images, language packages (npm, Python, Maven, Go), and OS packages. It replaces Container Registry (gcr.io).

## Repositories

### Create

```bash
# Docker repository
gcloud artifacts repositories create REPO_NAME \
  --repository-format=docker \
  --location=REGION \
  --description="Docker images"

# Python (PyPI) repository
gcloud artifacts repositories create REPO_NAME \
  --repository-format=python \
  --location=REGION

# npm repository
gcloud artifacts repositories create REPO_NAME \
  --repository-format=npm \
  --location=REGION

# Maven repository
gcloud artifacts repositories create REPO_NAME \
  --repository-format=maven \
  --location=REGION

# Go module repository
gcloud artifacts repositories create REPO_NAME \
  --repository-format=go \
  --location=REGION

# Remote repository (proxy to upstream like Docker Hub)
gcloud artifacts repositories create REPO_NAME \
  --repository-format=docker \
  --location=REGION \
  --mode=remote-repository \
  --remote-docker-repo=DOCKER-HUB

# Virtual repository (aggregates multiple repos)
gcloud artifacts repositories create REPO_NAME \
  --repository-format=docker \
  --location=REGION \
  --mode=virtual-repository
```

### Manage

```bash
# List repositories
gcloud artifacts repositories list
gcloud artifacts repositories list --location=REGION

# Describe
gcloud artifacts repositories describe REPO_NAME --location=REGION

# Delete
gcloud artifacts repositories delete REPO_NAME --location=REGION

# Update
gcloud artifacts repositories update REPO_NAME --location=REGION \
  --description="Updated description"
```

## Docker images

### Authentication

```bash
# Configure Docker to authenticate to Artifact Registry
gcloud auth configure-docker REGION-docker.pkg.dev

# Multiple regions
gcloud auth configure-docker us-central1-docker.pkg.dev,us-east1-docker.pkg.dev
```

### Push and pull

```bash
# Tag an image for Artifact Registry
docker tag SOURCE_IMAGE REGION-docker.pkg.dev/PROJECT/REPO/IMAGE:TAG

# Push
docker push REGION-docker.pkg.dev/PROJECT/REPO/IMAGE:TAG

# Pull
docker pull REGION-docker.pkg.dev/PROJECT/REPO/IMAGE:TAG
```

### List and manage images

```bash
# List images in a repository
gcloud artifacts docker images list REGION-docker.pkg.dev/PROJECT/REPO

# List tags
gcloud artifacts docker tags list REGION-docker.pkg.dev/PROJECT/REPO/IMAGE

# Describe an image (vulnerability info, metadata)
gcloud artifacts docker images describe \
  REGION-docker.pkg.dev/PROJECT/REPO/IMAGE:TAG

# Delete an image
gcloud artifacts docker images delete \
  REGION-docker.pkg.dev/PROJECT/REPO/IMAGE:TAG

# Delete untagged images
gcloud artifacts docker images list REGION-docker.pkg.dev/PROJECT/REPO \
  --include-tags --filter="NOT tags:*" \
  --format="value(package)" | while read -r img; do
  gcloud artifacts docker images delete "$img" --quiet
done
```

## Package management

### Python (PyPI)

```bash
# Configure pip
gcloud artifacts print-settings python \
  --repository=REPO --location=REGION --project=PROJECT

# Install from Artifact Registry
pip install --index-url https://REGION-python.pkg.dev/PROJECT/REPO/simple/ PACKAGE

# Upload with twine
twine upload --repository-url https://REGION-python.pkg.dev/PROJECT/REPO/ dist/*
```

### npm

```bash
# Configure npm
gcloud artifacts print-settings npm \
  --repository=REPO --location=REGION --project=PROJECT

# Adds to .npmrc:
# @SCOPE:registry=https://REGION-npm.pkg.dev/PROJECT/REPO/
# //REGION-npm.pkg.dev/PROJECT/REPO/:always-auth=true

npm publish
```

### Maven

```bash
# Print settings for pom.xml / settings.xml
gcloud artifacts print-settings mvn \
  --repository=REPO --location=REGION --project=PROJECT
```

## Cleanup policies

```bash
# Set a cleanup policy (delete images older than N days)
gcloud artifacts repositories set-cleanup-policies REPO_NAME \
  --location=REGION \
  --policy=policy.json
```

### policy.json

```json
[{
  "name": "delete-old-images",
  "action": {"type": "Delete"},
  "condition": {
    "olderThan": "2592000s"
  }
}]
```

## IAM

```bash
# Grant read access
gcloud artifacts repositories add-iam-policy-binding REPO_NAME \
  --location=REGION \
  --member="serviceAccount:SA_EMAIL" \
  --role="roles/artifactregistry.reader"

# Grant write access
gcloud artifacts repositories add-iam-policy-binding REPO_NAME \
  --location=REGION \
  --member="serviceAccount:SA_EMAIL" \
  --role="roles/artifactregistry.writer"
```

## Troubleshooting

- **"Permission denied" on push** — run `gcloud auth configure-docker` and ensure the account has `roles/artifactregistry.writer`
- **"Repository not found"** — verify region, project, and repo name in the image URL
- **Migration from gcr.io** — Artifact Registry supports `gcr.io` routing; enable with `gcloud artifacts settings enable-upgrade-redirection`
- **Large images** — check cleanup policies to manage storage costs
- **Authentication expired** — re-run `gcloud auth configure-docker REGION-docker.pkg.dev`
