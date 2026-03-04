# gcloud sql — Cloud SQL Reference

## Contents
- [Overview](#overview)
- [Instances](#instances)
- [Databases](#databases)
- [Users](#users)
- [Connect](#connect)
- [Authorized networks (public IP access)](#authorized-networks-public-ip-access)
- [Backups](#backups)
- [Export and import](#export-and-import)
- [Replicas](#replicas)
- [Troubleshooting](#troubleshooting)

## Overview

Cloud SQL provides managed relational databases: **MySQL**, **PostgreSQL**, and **SQL Server**. Google handles replication, backups, patching, and failover.

## Instances

### Create

```bash
# PostgreSQL
gcloud sql instances create INSTANCE_NAME \
  --database-version=POSTGRES_16 \
  --tier=db-custom-2-8192 \
  --region=REGION \
  --root-password=PASSWORD

# MySQL
gcloud sql instances create INSTANCE_NAME \
  --database-version=MYSQL_8_0 \
  --tier=db-n1-standard-2 \
  --region=REGION \
  --root-password=PASSWORD

# SQL Server
gcloud sql instances create INSTANCE_NAME \
  --database-version=SQLSERVER_2022_STANDARD \
  --tier=db-custom-2-8192 \
  --region=REGION \
  --root-password=PASSWORD

# With high availability
gcloud sql instances create INSTANCE_NAME \
  --database-version=POSTGRES_16 \
  --tier=db-custom-4-16384 \
  --region=REGION \
  --availability-type=REGIONAL \
  --root-password=PASSWORD

# Private IP only (no public IP)
gcloud sql instances create INSTANCE_NAME \
  --database-version=POSTGRES_16 \
  --tier=db-custom-2-8192 \
  --region=REGION \
  --network=VPC_NETWORK \
  --no-assign-ip \
  --root-password=PASSWORD
```

**Common flags:**
- `--tier` — machine type (e.g., `db-f1-micro`, `db-custom-CPU-MEMORY`)
- `--storage-size` — disk size in GB (e.g., `100GB`)
- `--storage-type` — `SSD` or `HDD`
- `--storage-auto-increase` — auto-increase disk when full
- `--availability-type` — `ZONAL` (default) or `REGIONAL` (HA)
- `--backup-start-time` — e.g., `04:00` (UTC)
- `--enable-bin-log` — enable binary logging (MySQL, required for replicas)
- `--maintenance-window-day` / `--maintenance-window-hour` — preferred maintenance window
- `--database-flags` — set database flags (e.g., `--database-flags=max_connections=200`)

### Manage

```bash
# List instances
gcloud sql instances list

# Describe
gcloud sql instances describe INSTANCE_NAME

# Restart
gcloud sql instances restart INSTANCE_NAME

# Patch (update settings)
gcloud sql instances patch INSTANCE_NAME \
  --tier=db-custom-4-16384 \
  --storage-size=200GB

# Delete
gcloud sql instances delete INSTANCE_NAME
```

## Databases

```bash
# Create a database
gcloud sql databases create DB_NAME --instance=INSTANCE_NAME
gcloud sql databases create DB_NAME --instance=INSTANCE_NAME --charset=UTF8

# List databases
gcloud sql databases list --instance=INSTANCE_NAME

# Delete
gcloud sql databases delete DB_NAME --instance=INSTANCE_NAME
```

## Users

```bash
# Create a user
gcloud sql users create USER_NAME --instance=INSTANCE_NAME \
  --password=PASSWORD

# For PostgreSQL (specify host is optional)
gcloud sql users create USER_NAME --instance=INSTANCE_NAME \
  --password=PASSWORD

# List users
gcloud sql users list --instance=INSTANCE_NAME

# Set password
gcloud sql users set-password USER_NAME --instance=INSTANCE_NAME \
  --password=NEW_PASSWORD

# Delete
gcloud sql users delete USER_NAME --instance=INSTANCE_NAME
```

## Connect

```bash
# Connect via Cloud SQL Auth Proxy built into gcloud
gcloud sql connect INSTANCE_NAME --user=USER_NAME
gcloud sql connect INSTANCE_NAME --user=USER_NAME --database=DB_NAME

# Cloud SQL Auth Proxy (for applications)
# Download: https://cloud.google.com/sql/docs/mysql/sql-proxy
cloud-sql-proxy PROJECT:REGION:INSTANCE --port=5432

# Connect using private IP
gcloud sql connect INSTANCE_NAME --user=USER_NAME
```

## Authorized networks (public IP access)

```bash
# Authorize an IP range
gcloud sql instances patch INSTANCE_NAME \
  --authorized-networks=IP_ADDRESS/CIDR

# Authorize multiple
gcloud sql instances patch INSTANCE_NAME \
  --authorized-networks="10.0.0.1/32,203.0.113.0/24"

# Clear all authorized networks
gcloud sql instances patch INSTANCE_NAME --clear-authorized-networks
```

## Backups

```bash
# Create an on-demand backup
gcloud sql backups create --instance=INSTANCE_NAME

# List backups
gcloud sql backups list --instance=INSTANCE_NAME

# Describe
gcloud sql backups describe BACKUP_ID --instance=INSTANCE_NAME

# Restore from backup
gcloud sql backups restore BACKUP_ID --restore-instance=INSTANCE_NAME

# Delete
gcloud sql backups delete BACKUP_ID --instance=INSTANCE_NAME
```

## Export and import

```bash
# Export to GCS (SQL dump)
gcloud sql export sql INSTANCE_NAME gs://BUCKET/dump.sql \
  --database=DB_NAME

# Export to GCS (CSV)
gcloud sql export csv INSTANCE_NAME gs://BUCKET/data.csv \
  --database=DB_NAME --query="SELECT * FROM table_name"

# Import from GCS
gcloud sql import sql INSTANCE_NAME gs://BUCKET/dump.sql \
  --database=DB_NAME

gcloud sql import csv INSTANCE_NAME gs://BUCKET/data.csv \
  --database=DB_NAME --table=TABLE_NAME
```

## Replicas

```bash
# Create a read replica
gcloud sql instances create REPLICA_NAME \
  --master-instance-name=INSTANCE_NAME \
  --region=REGION

# Promote a replica to standalone
gcloud sql instances promote-replica REPLICA_NAME

# List replicas
gcloud sql instances list --filter="instanceType=READ_REPLICA_INSTANCE"
```

## Troubleshooting

- **Cannot connect** — check authorized networks for public IP; use Cloud SQL Auth Proxy for secure connections
- **"Connection refused"** — verify instance is running with `gcloud sql instances describe`
- **Storage full** — enable `--storage-auto-increase` or manually increase with `instances patch`
- **Slow queries** — check `--database-flags` for tuning; enable slow query logging
- **Backup failures** — check operation logs with `gcloud sql operations list --instance=INSTANCE_NAME`
- **Replica lag** — monitor with `gcloud sql instances describe REPLICA --format="value(replicaConfiguration)"`
