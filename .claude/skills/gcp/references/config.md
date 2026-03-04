# gcloud config — CLI Configuration & Named Configurations Reference

## Contents
- [Overview](#overview)
- [Properties](#properties)
- [Named Configurations](#named-configurations)
- [Environment Variable Overrides](#environment-variable-overrides)
- [Configuration File Locations](#configuration-file-locations)
- [Troubleshooting](#troubleshooting)

## Overview

`gcloud config` manages properties that control the behavior of the gcloud CLI. Properties are organized into sections (e.g., `core`, `compute`, `functions`) and can be scoped to named configurations for switching between projects/accounts quickly.

## Properties

### Set and unset

```bash
# Set a property
gcloud config set SECTION/PROPERTY VALUE
gcloud config set project MY_PROJECT          # core/project shorthand
gcloud config set compute/region us-central1
gcloud config set compute/zone us-central1-a
gcloud config set functions/gen2 true
gcloud config set run/region us-central1

# Unset a property
gcloud config unset SECTION/PROPERTY
gcloud config unset compute/zone
gcloud config unset auth/impersonate_service_account
```

### Common properties

| Property | Description |
|----------|-------------|
| `core/project` (or just `project`) | Default GCP project |
| `core/account` (or just `account`) | Default account |
| `compute/region` | Default Compute Engine region |
| `compute/zone` | Default Compute Engine zone |
| `run/region` | Default Cloud Run region |
| `functions/region` | Default Cloud Functions region |
| `functions/gen2` | Default to Gen2 functions (`true`/`false`) |
| `auth/impersonate_service_account` | Default SA to impersonate |
| `accessibility/screen_reader` | Enable screen reader mode |
| `core/disable_usage_reporting` | Disable anonymous usage stats |

### View current configuration

```bash
gcloud config list                              # All set properties
gcloud config list --all                        # All properties including unset
gcloud config list project                      # Specific property
gcloud config get-value project                 # Just the value
gcloud config get-value compute/region
```

## Named Configurations

Named configurations let you maintain separate sets of properties (e.g., per-project or per-environment).

### Create and activate

```bash
# Create a new configuration
gcloud config configurations create my-staging
gcloud config configurations create my-prod

# Activate a configuration
gcloud config configurations activate my-staging

# Set properties on the active configuration
gcloud config set project staging-project-id
gcloud config set compute/region us-east1
```

### List and describe

```bash
gcloud config configurations list
gcloud config configurations describe my-staging
```

### Delete

```bash
gcloud config configurations delete my-staging
```

### Override per-command

```bash
# Use a specific configuration for one command
gcloud compute instances list --configuration=my-prod

# Override via environment variable
export CLOUDSDK_ACTIVE_CONFIG_NAME=my-prod
gcloud config list
```

## Environment Variable Overrides

Any property can be overridden by an environment variable named `CLOUDSDK_SECTION_PROPERTY`:

```bash
export CLOUDSDK_CORE_PROJECT=my-other-project
export CLOUDSDK_COMPUTE_REGION=europe-west1
export CLOUDSDK_COMPUTE_ZONE=europe-west1-b
```

These take precedence over configuration file values.

## Configuration File Locations

- Active config name: `~/.config/gcloud/active_config`
- Config properties: `~/.config/gcloud/configurations/config_CONFIGNAME`
- Credentials: `~/.config/gcloud/credentials.db`
- ADC: `~/.config/gcloud/application_default_credentials.json`

## Troubleshooting

- **Wrong project/region** — check `gcloud config list` and verify active configuration with `gcloud config configurations list`
- **Unexpected behavior** — check for `CLOUDSDK_*` environment variables overriding config
- **Multiple environments** — use named configurations rather than constantly re-setting properties
- **Verify everything** — `gcloud info` shows active config, account, project, SDK paths, and Python version
