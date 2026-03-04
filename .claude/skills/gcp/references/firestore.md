# gcloud firestore — Firestore Database Reference

## Contents
- [Overview](#overview)
- [Databases](#databases)
- [Indexes](#indexes)
- [Export and import](#export-and-import)
- [Operations](#operations)
- [Required APIs](#required-apis)
- [Common patterns](#common-patterns)
- [Troubleshooting](#troubleshooting)

## Overview

Firestore is a serverless NoSQL document database. It supports Native mode (document/collection model with real-time listeners) and Datastore mode (entity/kind model, backward-compatible with Datastore). The `gcloud firestore` commands manage databases, indexes, and operations.

## Databases

```bash
# Create a database (default database)
gcloud firestore databases create --location=LOCATION
gcloud firestore databases create --location=nam5 --type=firestore-native

# Create a named database (multi-database support)
gcloud firestore databases create --database=my-db --location=LOCATION

# Datastore mode
gcloud firestore databases create --location=LOCATION --type=datastore-mode

# List databases
gcloud firestore databases list

# Describe
gcloud firestore databases describe
gcloud firestore databases describe --database=my-db

# Update (e.g., enable point-in-time recovery)
gcloud firestore databases update --type=firestore-native

# Delete a named database
gcloud firestore databases delete --database=my-db
```

**Locations:** Multi-region (`nam5`, `eur3`) or single region (`us-central1`, `europe-west1`, etc.)

## Indexes

Firestore auto-creates single-field indexes. Composite indexes must be defined explicitly.

```bash
# Create a composite index
gcloud firestore indexes composite create \
  --collection-group=COLLECTION \
  --field-config=field-path=field1,order=ascending \
  --field-config=field-path=field2,order=descending

# List indexes
gcloud firestore indexes composite list
gcloud firestore indexes fields list

# Describe
gcloud firestore indexes composite describe INDEX_ID

# Delete an index
gcloud firestore indexes composite delete INDEX_ID

# Deploy indexes from file
gcloud firestore indexes composite create --file=firestore.indexes.json
```

### firestore.indexes.json

```json
{
  "indexes": [
    {
      "collectionGroup": "users",
      "fields": [
        {"fieldPath": "status", "order": "ASCENDING"},
        {"fieldPath": "createdAt", "order": "DESCENDING"}
      ]
    }
  ]
}
```

## Export and import

```bash
# Export all data to GCS
gcloud firestore export gs://BUCKET/PATH

# Export specific collections
gcloud firestore export gs://BUCKET/PATH \
  --collection-ids=users,orders

# Import from GCS
gcloud firestore import gs://BUCKET/PATH

# List operations (exports/imports)
gcloud firestore operations list

# Cancel an operation
gcloud firestore operations cancel OPERATION_ID
```

## Operations

```bash
# List long-running operations
gcloud firestore operations list

# Describe
gcloud firestore operations describe OPERATION_ID

# Cancel
gcloud firestore operations cancel OPERATION_ID
```

## Required APIs

```bash
gcloud services enable firestore.googleapis.com
```

## Common patterns

### Backup strategy

```bash
# Scheduled export (use Cloud Scheduler + Cloud Function)
gcloud firestore export gs://BUCKET/backups/$(date +%Y-%m-%d)

# Or use Cloud Scheduler directly
gcloud scheduler jobs create http firestore-backup \
  --schedule="0 2 * * *" \
  --uri="https://firestore.googleapis.com/v1/projects/PROJECT/databases/(default)/exportDocuments" \
  --http-method=POST \
  --oauth-service-account-email=SA_EMAIL \
  --headers="Content-Type=application/json" \
  --message-body='{"outputUriPrefix":"gs://BUCKET/backups"}'
```

### Security rules deployment (Firebase CLI)

Firestore security rules are managed via the Firebase CLI, not gcloud:
```bash
firebase deploy --only firestore:rules
firebase deploy --only firestore:indexes
```

## Troubleshooting

- **"Database already exists"** — each project can have one `(default)` database; additional databases require unique names
- **"Index not found"** — composite queries need composite indexes; Firestore error messages include a direct link to create the required index
- **Export/import slow** — large databases take time; monitor with `gcloud firestore operations list`
- **Datastore vs Native mode** — cannot change mode after creation; create a new database if needed
- **Permission denied** — ensure the service account has `roles/datastore.user` or `roles/datastore.owner`
