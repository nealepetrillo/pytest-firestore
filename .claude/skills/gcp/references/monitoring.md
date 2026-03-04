# gcloud monitoring — Cloud Monitoring Reference

## Contents
- [Overview](#overview)
- [Dashboards](#dashboards)
- [Alerting policies](#alerting-policies)
- [Notification channels](#notification-channels)
- [Uptime checks](#uptime-checks)
- [Metrics](#metrics)
- [Snooze alerts](#snooze-alerts)
- [Troubleshooting](#troubleshooting)

## Overview

Cloud Monitoring (formerly Stackdriver Monitoring) provides visibility into GCP resource performance, uptime, and health. It covers metrics, dashboards, alerting policies, uptime checks, and notification channels.

## Dashboards

```bash
# List dashboards
gcloud monitoring dashboards list
gcloud monitoring dashboards list --format="table(name,displayName)"

# Describe a dashboard
gcloud monitoring dashboards describe DASHBOARD_ID

# Create from JSON file
gcloud monitoring dashboards create --config-from-file=dashboard.json

# Update
gcloud monitoring dashboards update DASHBOARD_ID \
  --config-from-file=dashboard.json

# Delete
gcloud monitoring dashboards delete DASHBOARD_ID
```

### Dashboard JSON structure

```json
{
  "displayName": "My Service Dashboard",
  "gridLayout": {
    "widgets": [
      {
        "title": "CPU Utilization",
        "xyChart": {
          "dataSets": [{
            "timeSeriesQuery": {
              "timeSeriesFilter": {
                "filter": "metric.type=\"compute.googleapis.com/instance/cpu/utilization\"",
                "aggregation": {
                  "alignmentPeriod": "60s",
                  "perSeriesAligner": "ALIGN_MEAN"
                }
              }
            }
          }]
        }
      }
    ]
  }
}
```

## Alerting policies

```bash
# List alert policies
gcloud alpha monitoring policies list
gcloud alpha monitoring policies list --format="table(name,displayName,enabled)"

# Describe
gcloud alpha monitoring policies describe POLICY_ID

# Create from JSON file
gcloud alpha monitoring policies create --policy-from-file=policy.json

# Update
gcloud alpha monitoring policies update POLICY_ID \
  --policy-from-file=policy.json

# Enable / disable
gcloud alpha monitoring policies update POLICY_ID --enabled
gcloud alpha monitoring policies update POLICY_ID --no-enabled

# Delete
gcloud alpha monitoring policies delete POLICY_ID
```

### Alert policy JSON structure

```json
{
  "displayName": "High CPU Alert",
  "conditions": [{
    "displayName": "CPU above 80%",
    "conditionThreshold": {
      "filter": "metric.type=\"compute.googleapis.com/instance/cpu/utilization\"",
      "comparison": "COMPARISON_GT",
      "thresholdValue": 0.8,
      "duration": "300s",
      "aggregations": [{
        "alignmentPeriod": "60s",
        "perSeriesAligner": "ALIGN_MEAN"
      }]
    }
  }],
  "notificationChannels": ["projects/PROJECT/notificationChannels/CHANNEL_ID"],
  "combiner": "OR"
}
```

## Notification channels

```bash
# List channels
gcloud alpha monitoring channels list
gcloud alpha monitoring channels list \
  --format="table(name,type,displayName)"

# Create an email channel
gcloud alpha monitoring channels create \
  --type=email \
  --display-name="Ops Team Email" \
  --channel-labels=email_address=ops@example.com

# Create a Slack channel
gcloud alpha monitoring channels create \
  --type=slack \
  --display-name="Ops Slack" \
  --channel-labels=channel_name=#alerts,auth_token=TOKEN

# Describe
gcloud alpha monitoring channels describe CHANNEL_ID

# Delete
gcloud alpha monitoring channels delete CHANNEL_ID
```

## Uptime checks

```bash
# List uptime checks
gcloud monitoring uptime list-configs

# Create an HTTP uptime check
gcloud monitoring uptime create DISPLAY_NAME \
  --resource-type=uptime-url \
  --hostname=www.example.com \
  --path=/ \
  --protocol=https \
  --period=300

# Describe
gcloud monitoring uptime describe CHECK_ID

# Delete
gcloud monitoring uptime delete CHECK_ID
```

## Metrics

```bash
# List available metric types
gcloud monitoring metrics list --filter="metric.type:compute.googleapis.com"

# Describe a metric
gcloud monitoring metrics describe compute.googleapis.com/instance/cpu/utilization

# Write custom metrics (via API or client libraries)
# Custom metric type format: custom.googleapis.com/my_metric
```

### Common metric types

| Metric | Description |
|--------|-------------|
| `compute.googleapis.com/instance/cpu/utilization` | VM CPU usage |
| `compute.googleapis.com/instance/disk/read_bytes_count` | Disk read bytes |
| `run.googleapis.com/request_count` | Cloud Run request count |
| `run.googleapis.com/request_latencies` | Cloud Run latency |
| `cloudsql.googleapis.com/database/cpu/utilization` | Cloud SQL CPU |
| `cloudsql.googleapis.com/database/disk/utilization` | Cloud SQL disk |
| `loadbalancing.googleapis.com/https/request_count` | LB request count |
| `pubsub.googleapis.com/subscription/num_undelivered_messages` | Pub/Sub backlog |

## Snooze alerts

```bash
# Snooze an alert policy
gcloud alpha monitoring snoozes create \
  --display-name="Maintenance window" \
  --criteria-policies=POLICY_ID \
  --start-time="2025-06-01T00:00:00Z" \
  --end-time="2025-06-01T06:00:00Z"
```

## Troubleshooting

- **No metrics data** — check that the monitored resource exists and the Monitoring API is enabled
- **Alert not firing** — verify condition threshold, duration, and that the policy is enabled
- **Notification not received** — check notification channel configuration and verify the channel with a test
- **Dashboard empty** — verify metric filter syntax; check the time range in the dashboard
- **Custom metrics not appearing** — custom metrics can take a few minutes to appear; verify metric descriptor exists
