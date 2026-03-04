---
name: gcloud-cli
description: >
  Comprehensive reference for the Google Cloud CLI (gcloud). Use this skill whenever
  working with GCP infrastructure, services, or tooling via the command line. Triggers
  include: any mention of "gcloud", "Google Cloud", "GCP", Cloud Functions, Cloud Run,
  Compute Engine, IAM, service accounts, authentication with Google Cloud, ADC
  (Application Default Credentials), GCP emulators (Firestore, Pub/Sub, Bigtable,
  Datastore, Spanner), or any task requiring interaction with Google Cloud Platform
  from a terminal. Also use when deploying to GCP, managing GCP projects/configs,
  or debugging GCP authentication issues.
---

# gcloud CLI Skill

Provide accurate, up-to-date guidance for using the `gcloud` command-line tool to manage Google Cloud Platform resources and services.

## General gcloud Patterns

All gcloud commands follow: `gcloud [GROUP] [SUBGROUP] [COMMAND] [FLAGS]`

Common global flags available on every command:
- `--project PROJECT_ID` — override active project
- `--account ACCOUNT` — override active account
- `--format FORMAT` — output as json, yaml, csv, table, text, value, etc.
- `--quiet` / `-q` — disable interactive prompts
- `--impersonate-service-account SA_EMAIL` — run as a service account without a key file
- `--verbosity LEVEL` — debug, info, warning, error, critical, none
- `--configuration CONFIG` — use a named configuration

### Configurations

Manage multiple project/account/region profiles:
```
gcloud config configurations create NAME
gcloud config configurations activate NAME
gcloud config set project PROJECT_ID
gcloud config set compute/region REGION
gcloud config set compute/zone ZONE
gcloud config list
```

## Top-Level Command Groups

| Group | Purpose | Reference |
|-------|---------|-----------|
| `auth` | Authentication & credentials | `references/auth.md` |
| `config` | CLI configuration & named configurations | `references/config.md` |
| `projects` | Manage GCP projects | `references/projects.md` |
| `iam` | IAM roles, policies, service accounts | `references/iam.md` |
| `compute` | VMs, disks, networks, firewalls, load balancers | `references/compute.md` |
| `container` | GKE clusters and node pools | `references/container.md` |
| `functions` | Cloud Functions (deploy, call, logs) | `references/functions-and-run.md` |
| `run` | Cloud Run services and jobs | `references/functions-and-run.md` |
| `app` | App Engine applications | `references/app.md` |
| `builds` | Cloud Build triggers and submissions | `references/builds.md` |
| `storage` | Cloud Storage buckets and objects (also `gsutil`) | `references/storage.md` |
| `firestore` | Firestore databases and indexes | `references/firestore.md` |
| `pubsub` | Pub/Sub topics and subscriptions | `references/pubsub.md` |
| `sql` | Cloud SQL instances | `references/sql.md` |
| `secrets` | Secret Manager | `references/secrets.md` |
| `logging` | Cloud Logging read/write | `references/logging.md` |
| `monitoring` | Cloud Monitoring dashboards and alerts | `references/monitoring.md` |
| `artifacts` | Artifact Registry repos | `references/artifacts.md` |
| `dns` | Cloud DNS zones and records | `references/dns.md` |
| `kms` | Cloud KMS keys | `references/kms.md` |
| `emulators` | Local dev emulators | `references/emulators.md` |
| `services` | Enable/disable APIs (`gcloud services enable ...`) | `references/services.md` |
| `components` | Manage SDK components (`gcloud components install ...`) | `references/components.md` |

Bundled sub-tools: `bq` (BigQuery), `gsutil` (Cloud Storage), `kubectl` (Kubernetes).

## Common Workflows

### Deploy a Cloud Function (Gen2)
```bash
gcloud functions deploy FUNCTION_NAME \
  --gen2 --runtime python312 --trigger-http \
  --allow-unauthenticated --region REGION \
  --source . --entry-point main
```

### Deploy to Cloud Run
```bash
gcloud run deploy SERVICE_NAME \
  --image IMAGE_URL --region REGION \
  --allow-unauthenticated --set-env-vars KEY=VALUE
```

### Enable an API
```bash
gcloud services enable firestore.googleapis.com
gcloud services list --enabled
```

### Create a service account and grant roles
```bash
gcloud iam service-accounts create SA_NAME --display-name "Description"
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:SA_NAME@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/ROLE"
```

## Troubleshooting

- `gcloud info` — active config, account, project, SDK paths, Python version
- `gcloud auth list` — all credentialed accounts and which is active
- `gcloud config list` — active configuration values
- If ADC issues, check `GOOGLE_APPLICATION_CREDENTIALS` env var and run `gcloud auth application-default login`
- `--log-http` on any command to see raw HTTP requests/responses
- `--verbosity debug` for maximum diagnostic output
