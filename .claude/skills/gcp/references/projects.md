# gcloud projects — Project Management Reference

## Contents
- [Overview](#overview)
- [Create and manage](#create-and-manage)
- [Project properties](#project-properties)
- [Set active project](#set-active-project)
- [Organization and folders](#organization-and-folders)
- [Labels](#labels)
- [Billing](#billing)
- [Troubleshooting](#troubleshooting)

## Overview

GCP projects are the top-level organizing entity. All resources belong to a project, and billing, APIs, and IAM are managed at the project level.

## Create and manage

```bash
# Create a project
gcloud projects create PROJECT_ID \
  --name="Human-Readable Name" \
  --organization=ORG_ID \
  --folder=FOLDER_ID

# List projects
gcloud projects list
gcloud projects list --format="table(projectId,name,projectNumber)"
gcloud projects list --filter="name:staging"
gcloud projects list --sort-by=createTime

# Describe a project
gcloud projects describe PROJECT_ID

# Update project name
gcloud projects update PROJECT_ID --name="New Name"

# Delete a project (30-day recovery window)
gcloud projects delete PROJECT_ID

# Undelete (within 30 days)
gcloud projects undelete PROJECT_ID
```

## Project properties

```bash
# Get project number from project ID
gcloud projects describe PROJECT_ID --format="value(projectNumber)"

# Get project ID from project number
gcloud projects list --filter="projectNumber=123456789" --format="value(projectId)"

# Get current project
gcloud config get-value project
```

## Set active project

```bash
gcloud config set project PROJECT_ID

# Override per-command
gcloud compute instances list --project=OTHER_PROJECT
```

## Organization and folders

```bash
# List organizations
gcloud organizations list

# Describe organization
gcloud organizations describe ORG_ID

# List folders
gcloud resource-manager folders list --organization=ORG_ID
gcloud resource-manager folders list --folder=PARENT_FOLDER_ID

# Create a folder
gcloud resource-manager folders create --display-name="Engineering" \
  --organization=ORG_ID

# Move a project to a folder
gcloud projects move PROJECT_ID --folder=FOLDER_ID
```

## Labels

Labels are key-value pairs for organizing and filtering projects.

```bash
# Add labels
gcloud projects update PROJECT_ID \
  --update-labels=env=staging,team=backend

# Remove labels
gcloud projects update PROJECT_ID \
  --remove-labels=env,team

# Filter by labels
gcloud projects list --filter="labels.env=production"
```

## Billing

```bash
# List billing accounts
gcloud billing accounts list

# Link project to billing account
gcloud billing projects link PROJECT_ID \
  --billing-account=BILLING_ACCOUNT_ID

# Check billing status
gcloud billing projects describe PROJECT_ID
```

## Troubleshooting

- **"Project not found"** — verify project ID (not name), check you have access with `gcloud projects list`
- **"Billing must be enabled"** — link a billing account before enabling paid APIs
- **Deleted project** — use `gcloud projects undelete` within 30 days
- **Quota/limits** — default project quota is limited per organization; request increases via Cloud Console
