# gcloud pubsub — Pub/Sub Messaging Reference

## Contents
- [Overview](#overview)
- [Topics](#topics)
- [Subscriptions](#subscriptions)
- [Snapshots](#snapshots)
- [Schemas](#schemas)
- [IAM](#iam)
- [Troubleshooting](#troubleshooting)

## Overview

Pub/Sub is a fully managed real-time messaging service. Publishers send messages to **topics**, and subscribers receive them via **subscriptions** (pull or push). Messages are retained until acknowledged.

## Topics

```bash
# Create a topic
gcloud pubsub topics create TOPIC_NAME

# Create with a schema
gcloud pubsub topics create TOPIC_NAME \
  --schema=SCHEMA_NAME --message-encoding=JSON

# Create with message retention
gcloud pubsub topics create TOPIC_NAME \
  --message-retention-duration=7d

# List topics
gcloud pubsub topics list
gcloud pubsub topics list --format="value(name)"

# Describe
gcloud pubsub topics describe TOPIC_NAME

# Delete
gcloud pubsub topics delete TOPIC_NAME

# Publish a message
gcloud pubsub topics publish TOPIC_NAME --message="Hello World"
gcloud pubsub topics publish TOPIC_NAME \
  --message="data" \
  --attribute=key1=value1,key2=value2
```

## Subscriptions

### Create

```bash
# Pull subscription
gcloud pubsub subscriptions create SUB_NAME --topic=TOPIC_NAME

# Push subscription (delivers to an endpoint)
gcloud pubsub subscriptions create SUB_NAME \
  --topic=TOPIC_NAME \
  --push-endpoint=https://my-service.run.app/push

# With authentication (for private Cloud Run/Functions)
gcloud pubsub subscriptions create SUB_NAME \
  --topic=TOPIC_NAME \
  --push-endpoint=https://my-service.run.app/push \
  --push-auth-service-account=SA_EMAIL

# With dead-letter topic
gcloud pubsub subscriptions create SUB_NAME \
  --topic=TOPIC_NAME \
  --dead-letter-topic=DLT_TOPIC \
  --max-delivery-attempts=5

# With message ordering
gcloud pubsub subscriptions create SUB_NAME \
  --topic=TOPIC_NAME \
  --enable-message-ordering

# With exactly-once delivery
gcloud pubsub subscriptions create SUB_NAME \
  --topic=TOPIC_NAME \
  --enable-exactly-once-delivery

# Custom ack deadline and retention
gcloud pubsub subscriptions create SUB_NAME \
  --topic=TOPIC_NAME \
  --ack-deadline=60 \
  --message-retention-duration=7d \
  --retain-acked-messages
```

### Manage

```bash
# List subscriptions
gcloud pubsub subscriptions list
gcloud pubsub subscriptions list --format="table(name,topic,pushConfig.pushEndpoint)"

# Describe
gcloud pubsub subscriptions describe SUB_NAME

# Update
gcloud pubsub subscriptions update SUB_NAME \
  --ack-deadline=120 \
  --push-endpoint=https://new-endpoint.run.app/push

# Delete
gcloud pubsub subscriptions delete SUB_NAME

# Pull messages
gcloud pubsub subscriptions pull SUB_NAME --limit=10
gcloud pubsub subscriptions pull SUB_NAME --auto-ack --limit=10

# Acknowledge a message
gcloud pubsub subscriptions ack SUB_NAME --ack-ids=ACK_ID

# Seek (replay messages)
gcloud pubsub subscriptions seek SUB_NAME --time=TIMESTAMP
gcloud pubsub subscriptions seek SUB_NAME --snapshot=SNAPSHOT_NAME
```

## Snapshots

```bash
# Create a snapshot
gcloud pubsub snapshots create SNAPSHOT_NAME --subscription=SUB_NAME

# List
gcloud pubsub snapshots list

# Delete
gcloud pubsub snapshots delete SNAPSHOT_NAME

# Seek to a snapshot (replay messages)
gcloud pubsub subscriptions seek SUB_NAME --snapshot=SNAPSHOT_NAME
```

## Schemas

```bash
# Create a schema (Avro or Protocol Buffer)
gcloud pubsub schemas create SCHEMA_NAME \
  --type=AVRO --definition-file=schema.avsc

gcloud pubsub schemas create SCHEMA_NAME \
  --type=PROTOCOL_BUFFER --definition-file=schema.proto

# List schemas
gcloud pubsub schemas list

# Describe
gcloud pubsub schemas describe SCHEMA_NAME

# Validate a message against a schema
gcloud pubsub schemas validate-message \
  --type=AVRO --definition-file=schema.avsc \
  --message-encoding=JSON --message='{"field":"value"}'

# Delete
gcloud pubsub schemas delete SCHEMA_NAME
```

## IAM

```bash
# Grant publish permission
gcloud pubsub topics add-iam-policy-binding TOPIC_NAME \
  --member="serviceAccount:SA_EMAIL" \
  --role="roles/pubsub.publisher"

# Grant subscribe permission
gcloud pubsub subscriptions add-iam-policy-binding SUB_NAME \
  --member="serviceAccount:SA_EMAIL" \
  --role="roles/pubsub.subscriber"
```

## Troubleshooting

- **Messages not received** — check subscription exists and is attached to the right topic; check push endpoint is reachable
- **Push delivery failures** — verify push endpoint returns 2xx; check push auth SA has invoke permissions on the target
- **Message backlog growing** — check consumer throughput; increase pull concurrency or push subscriber instances
- **Duplicate messages** — Pub/Sub has at-least-once delivery; use `--enable-exactly-once-delivery` for stronger guarantees
- **Dead-lettered messages** — check dead-letter topic subscription for failed messages; investigate why original processing failed
- **Ordering issues** — enable message ordering on subscription and publish with ordering key
