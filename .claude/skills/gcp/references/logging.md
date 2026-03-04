# gcloud logging — Cloud Logging Reference

## Contents
- [Overview](#overview)
- [Read logs](#read-logs)
- [Write logs](#write-logs)
- [Log sinks (exports)](#log-sinks-exports)
- [Log exclusions](#log-exclusions)
- [Log-based metrics](#log-based-metrics)
- [Troubleshooting](#troubleshooting)

## Overview

Cloud Logging (formerly Stackdriver Logging) collects, stores, and analyzes log data from GCP services and custom applications. Logs are organized by resource type, log name, and severity.

## Read logs

```bash
# Read recent logs
gcloud logging read --limit=50

# Read with a filter
gcloud logging read "severity>=ERROR" --limit=20
gcloud logging read "resource.type=cloud_run_revision" --limit=50
gcloud logging read 'resource.type="gce_instance" AND severity="ERROR"' --limit=20

# Filter by time
gcloud logging read 'timestamp>="2025-01-01T00:00:00Z"' --limit=100
gcloud logging read 'timestamp>="2025-01-01" AND timestamp<"2025-01-02"' --limit=100

# Filter by log name
gcloud logging read 'logName="projects/PROJECT/logs/my-log"' --limit=50

# Text search in payload
gcloud logging read 'textPayload:"error connecting"' --limit=20
gcloud logging read 'jsonPayload.message:"timeout"' --limit=20

# Combine filters
gcloud logging read \
  'resource.type="cloud_function" AND resource.labels.function_name="my-func" AND severity>=WARNING' \
  --limit=50

# Output as JSON
gcloud logging read "severity>=ERROR" --limit=10 --format=json

# Freshness (how recent, default 1 day)
gcloud logging read "severity>=ERROR" --freshness=7d --limit=100

# Order
gcloud logging read "severity>=ERROR" --order=asc --limit=50
```

### Common resource types

| Resource Type | Description |
|--------------|-------------|
| `cloud_run_revision` | Cloud Run |
| `cloud_function` | Cloud Functions |
| `gce_instance` | Compute Engine VM |
| `gke_container` | GKE container |
| `k8s_container` | Kubernetes container |
| `cloudsql_database` | Cloud SQL |
| `gae_app` | App Engine |
| `global` | Project-level / custom |

### Severity levels

`DEFAULT`, `DEBUG`, `INFO`, `NOTICE`, `WARNING`, `ERROR`, `CRITICAL`, `ALERT`, `EMERGENCY`

## Write logs

```bash
# Write a log entry
gcloud logging write LOG_NAME "Log message text"

# Write with severity
gcloud logging write LOG_NAME "Something failed" --severity=ERROR

# Write JSON payload
gcloud logging write LOG_NAME '{"message":"structured log","code":500}' \
  --payload-type=json --severity=ERROR
```

## Log sinks (exports)

Route logs to BigQuery, Cloud Storage, Pub/Sub, or another project.

```bash
# Create a sink to BigQuery
gcloud logging sinks create SINK_NAME \
  bigquery.googleapis.com/projects/PROJECT/datasets/DATASET \
  --log-filter='severity>=ERROR'

# Create a sink to Cloud Storage
gcloud logging sinks create SINK_NAME \
  storage.googleapis.com/BUCKET_NAME \
  --log-filter='resource.type="gce_instance"'

# Create a sink to Pub/Sub
gcloud logging sinks create SINK_NAME \
  pubsub.googleapis.com/projects/PROJECT/topics/TOPIC \
  --log-filter='severity>=WARNING'

# List sinks
gcloud logging sinks list

# Describe
gcloud logging sinks describe SINK_NAME

# Update filter
gcloud logging sinks update SINK_NAME \
  --log-filter='severity>=CRITICAL'

# Delete
gcloud logging sinks delete SINK_NAME
```

After creating a sink, grant the sink's service account write access to the destination:
```bash
# Get the sink writer identity
gcloud logging sinks describe SINK_NAME --format="value(writerIdentity)"
# Then grant it the appropriate role on the destination resource
```

## Log exclusions

```bash
# Exclude logs from ingestion (reduces cost)
gcloud logging sinks create _Default-exclusion \
  --log-filter='resource.type="gce_instance" AND severity=DEBUG' \
  --exclusion='name=exclude-debug,filter=severity=DEBUG'

# Create an exclusion on _Default sink
gcloud logging sinks update _Default \
  --add-exclusion='name=exclude-debug,filter=severity<=DEBUG'

# Remove an exclusion
gcloud logging sinks update _Default \
  --remove-exclusions=exclude-debug
```

## Log-based metrics

```bash
# Create a counter metric
gcloud logging metrics create METRIC_NAME \
  --description="Count of errors" \
  --log-filter='severity>=ERROR'

# List metrics
gcloud logging metrics list

# Describe
gcloud logging metrics describe METRIC_NAME

# Update
gcloud logging metrics update METRIC_NAME \
  --log-filter='severity>=CRITICAL'

# Delete
gcloud logging metrics delete METRIC_NAME
```

## Troubleshooting

- **No logs appearing** — check resource type and log name filters; verify `--freshness` is long enough
- **Missing logs** — check exclusion filters and retention policies; logs may be excluded by `_Default` sink exclusions
- **Sink not exporting** — verify sink writer identity has permission on the destination (BigQuery, GCS, Pub/Sub)
- **High logging costs** — use exclusion filters to drop verbose or low-value logs; reduce severity level of application logging
- **Query syntax** — Cloud Logging uses its own filter syntax, not SQL; see the Logging query language documentation
