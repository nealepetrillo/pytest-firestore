# gcloud components — SDK Component Management Reference

## Contents
- [Overview](#overview)
- [Install components](#install-components)
- [Update](#update)
- [Remove](#remove)
- [List components](#list-components)
- [Reinstall](#reinstall)
- [SDK version and info](#sdk-version-and-info)
- [Key components](#key-components)
- [Troubleshooting](#troubleshooting)

## Overview

`gcloud components` manages the installed components of the Google Cloud SDK. Components include CLI tools (gcloud, gsutil, bq), language extensions, emulators, and additional utilities.

## Install components

```bash
# Install a component
gcloud components install COMPONENT_ID

# Install multiple components
gcloud components install kubectl cloud-firestore-emulator pubsub-emulator

# Common components to install
gcloud components install kubectl                    # Kubernetes CLI
gcloud components install cloud-firestore-emulator   # Firestore emulator
gcloud components install pubsub-emulator            # Pub/Sub emulator
gcloud components install bigtable                   # Bigtable emulator + cbt tool
gcloud components install cloud-datastore-emulator   # Datastore emulator
gcloud components install cloud-spanner-emulator     # Spanner emulator
gcloud components install docker-credential-gcr      # Docker credential helper
gcloud components install gke-gcloud-auth-plugin     # GKE auth plugin for kubectl
gcloud components install app-engine-python          # App Engine Python
gcloud components install app-engine-go              # App Engine Go
gcloud components install beta                       # Beta commands
gcloud components install alpha                      # Alpha commands
```

## Update

```bash
# Update all components to the latest version
gcloud components update

# Update to a specific version
gcloud components update --version=VERSION
```

## Remove

```bash
# Remove a component
gcloud components remove COMPONENT_ID
gcloud components remove cloud-firestore-emulator
```

## List components

```bash
# List all installed and available components
gcloud components list

# Show only installed
gcloud components list --filter="state.name=Installed"

# Show only updatable
gcloud components list --filter="state.name='Update Available'"
```

## Reinstall

```bash
# Reinstall the SDK (fixes corrupted installations)
gcloud components reinstall
```

## SDK version and info

```bash
# Check SDK version
gcloud version

# Full environment info
gcloud info

# Show SDK root directory
gcloud info --format="value(installation.sdk_root)"
```

## Key components

| Component ID | Description |
|-------------|-------------|
| `gcloud` | Core CLI (always installed) |
| `gsutil` | Cloud Storage tool |
| `bq` | BigQuery tool |
| `kubectl` | Kubernetes CLI |
| `gke-gcloud-auth-plugin` | GKE kubectl auth plugin |
| `beta` | Beta gcloud commands |
| `alpha` | Alpha gcloud commands |
| `cloud-firestore-emulator` | Firestore local emulator |
| `pubsub-emulator` | Pub/Sub local emulator |
| `bigtable` | Bigtable emulator + cbt CLI |
| `cloud-datastore-emulator` | Datastore local emulator |
| `cloud-spanner-emulator` | Spanner local emulator |
| `docker-credential-gcr` | Docker credential helper for GCR |
| `app-engine-python` | App Engine Python component |
| `app-engine-java` | App Engine Java component |
| `app-engine-go` | App Engine Go component |
| `cloud-run-proxy` | Cloud Run local proxy |
| `terraform-tools` | Terraform integration |

## Troubleshooting

- **"Component not installed"** — run `gcloud components install COMPONENT_ID`
- **Update errors** — try `gcloud components update` or reinstall the SDK
- **Permission denied on update** — SDK installed via package manager (apt, brew) must be updated via that package manager, not `gcloud components`
- **Package manager installations** — if installed via `apt-get` or `snap`, use `apt-get update && apt-get install google-cloud-cli` instead of `gcloud components`
- **Check installation method** — `gcloud info` shows the installation type and SDK root
