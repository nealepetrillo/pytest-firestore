# gcloud app — App Engine Reference

## Contents
- [Overview](#overview)
- [Application setup](#application-setup)
- [Deploy](#deploy)
- [Versions and traffic](#versions-and-traffic)
- [Services](#services)
- [Logs and debugging](#logs-and-debugging)
- [Configuration files](#configuration-files)
- [Firewall rules](#firewall-rules)
- [Troubleshooting](#troubleshooting)

## Overview

App Engine is a fully managed serverless platform for web applications. It supports Standard (sandboxed, fast scale-to-zero) and Flexible (Docker-based, more customizable) environments. Configuration is driven by `app.yaml`.

## Application setup

```bash
# Create an App Engine application (once per project, choose region carefully — cannot change)
gcloud app create --region=REGION

# Describe the application
gcloud app describe
```

## Deploy

```bash
# Deploy from current directory (uses app.yaml)
gcloud app deploy

# Deploy a specific config file
gcloud app deploy app.yaml

# Deploy without promoting (does not receive traffic)
gcloud app deploy --no-promote

# Deploy a specific version
gcloud app deploy --version=v2

# Deploy multiple services
gcloud app deploy app.yaml dispatch.yaml cron.yaml

# Deploy with a service account
gcloud app deploy --service-account=SA_EMAIL

# Skip build cache
gcloud app deploy --no-cache
```

## Versions and traffic

```bash
# List versions
gcloud app versions list
gcloud app versions list --service=default

# Describe a version
gcloud app versions describe VERSION --service=SERVICE

# Split traffic between versions
gcloud app services set-traffic SERVICE \
  --splits=v1=0.7,v2=0.3

# Traffic splitting methods
gcloud app services set-traffic SERVICE \
  --splits=v1=0.5,v2=0.5 \
  --split-by=ip        # or cookie, random

# Route all traffic to a version
gcloud app services set-traffic SERVICE --splits=v2=1

# Start / stop a version
gcloud app versions start VERSION --service=SERVICE
gcloud app versions stop VERSION --service=SERVICE

# Delete old versions
gcloud app versions delete VERSION --service=SERVICE
```

## Services

```bash
# List services
gcloud app services list

# Describe a service
gcloud app services describe SERVICE

# Delete a service
gcloud app services delete SERVICE
```

## Logs and debugging

```bash
# Stream logs
gcloud app logs tail

# Read recent logs
gcloud app logs read --limit=50
gcloud app logs read --service=default --version=v1

# Open the app in a browser
gcloud app browse
gcloud app browse --service=SERVICE

# Open Cloud Console logs page
gcloud app open-console --logs
```

## Configuration files

### app.yaml (Standard)

```yaml
runtime: python312
service: default
instance_class: F2
automatic_scaling:
  min_instances: 0
  max_instances: 10
  target_cpu_utilization: 0.65
env_variables:
  KEY: "value"
handlers:
  - url: /static
    static_dir: static
  - url: /.*
    script: auto
```

### app.yaml (Flexible)

```yaml
runtime: python
env: flex
service: api
automatic_scaling:
  min_num_instances: 1
  max_num_instances: 20
resources:
  cpu: 2
  memory_gb: 4
  disk_size_gb: 20
env_variables:
  KEY: "value"
```

### Other config files

- `cron.yaml` — scheduled tasks
- `dispatch.yaml` — URL routing across services
- `queue.yaml` — task queue configuration
- `index.yaml` — Datastore index definitions

```bash
# Deploy specific config
gcloud app deploy cron.yaml
gcloud app deploy dispatch.yaml
```

## Firewall rules

```bash
# List rules
gcloud app firewall-rules list

# Create rule
gcloud app firewall-rules create PRIORITY \
  --source-range=IP_RANGE --action=ALLOW

# Default deny all
gcloud app firewall-rules update default --action=DENY
```

## Troubleshooting

- **"Application already exists"** — App Engine can only be created once per project; region cannot be changed
- **"Module not found"** — check `app.yaml` entrypoint and file structure
- **High costs from idle instances** — set `min_instances: 0` in `app.yaml` for standard; flexible has minimum 1 instance
- **Deployment stuck** — check `gcloud app operations list` for pending operations
- **502 errors** — check startup logs with `gcloud app logs read`; verify health check endpoint responds
- **Cannot delete default service** — delete the entire project or deploy a minimal placeholder
