# gcloud compute — Compute Engine Reference

## Contents
- [Overview](#overview)
- [Instances](#instances)
- [Disks](#disks)
- [Images](#images)
- [Networking](#networking)
- [Instance groups and autoscaling](#instance-groups-and-autoscaling)
- [Troubleshooting](#troubleshooting)

## Overview

Compute Engine provides VMs (instances), persistent disks, networking (VPCs, firewalls, load balancers), and related infrastructure. Commands are organized under `gcloud compute`.

## Instances

### Create

```bash
gcloud compute instances create INSTANCE_NAME \
  --zone=ZONE \
  --machine-type=MACHINE_TYPE \
  --image-family=IMAGE_FAMILY \
  --image-project=IMAGE_PROJECT \
  [OPTIONAL_FLAGS]

# Example: Debian VM
gcloud compute instances create my-vm \
  --zone=us-central1-a \
  --machine-type=e2-medium \
  --image-family=debian-12 \
  --image-project=debian-cloud

# With custom boot disk
gcloud compute instances create my-vm \
  --zone=us-central1-a \
  --machine-type=n2-standard-4 \
  --boot-disk-size=100GB \
  --boot-disk-type=pd-ssd \
  --image-family=ubuntu-2404-lts-amd64 \
  --image-project=ubuntu-os-cloud

# Preemptible / Spot VM (much cheaper, can be terminated)
gcloud compute instances create my-vm \
  --zone=us-central1-a \
  --machine-type=e2-medium \
  --provisioning-model=SPOT \
  --instance-termination-action=STOP
```

**Common flags:**
- `--machine-type` — e.g. `e2-micro`, `e2-medium`, `n2-standard-4`, `c2-standard-8`
- `--image-family` / `--image` — OS image
- `--image-project` — project hosting the image (e.g. `debian-cloud`, `ubuntu-os-cloud`)
- `--boot-disk-size` — e.g. `50GB`, `200GB`
- `--boot-disk-type` — `pd-standard`, `pd-ssd`, `pd-balanced`
- `--service-account` — SA for the VM
- `--scopes` — API scopes (prefer IAM roles over scopes)
- `--tags` — network tags for firewall rules
- `--metadata` — key=value pairs
- `--metadata-from-file` — key=filepath pairs (e.g. startup scripts)
- `--network` / `--subnet` — VPC network and subnet
- `--no-address` — no external IP (internal only)

### Startup scripts

```bash
gcloud compute instances create my-vm \
  --zone=us-central1-a \
  --machine-type=e2-medium \
  --image-family=debian-12 \
  --image-project=debian-cloud \
  --metadata-from-file=startup-script=./startup.sh

# Or inline
gcloud compute instances create my-vm \
  --zone=us-central1-a \
  --machine-type=e2-medium \
  --image-family=debian-12 \
  --image-project=debian-cloud \
  --metadata=startup-script='#!/bin/bash
apt-get update && apt-get install -y nginx'
```

### Manage instances

```bash
# List instances
gcloud compute instances list
gcloud compute instances list --filter="zone:us-central1-a"
gcloud compute instances list --filter="status=RUNNING"
gcloud compute instances list --format="table(name,zone,machineType,status,networkInterfaces[0].accessConfigs[0].natIP)"

# Describe
gcloud compute instances describe INSTANCE --zone=ZONE

# Start / stop / reset / suspend / resume
gcloud compute instances start INSTANCE --zone=ZONE
gcloud compute instances stop INSTANCE --zone=ZONE
gcloud compute instances reset INSTANCE --zone=ZONE
gcloud compute instances suspend INSTANCE --zone=ZONE
gcloud compute instances resume INSTANCE --zone=ZONE

# Delete
gcloud compute instances delete INSTANCE --zone=ZONE

# Resize machine type (must stop first)
gcloud compute instances stop INSTANCE --zone=ZONE
gcloud compute instances set-machine-type INSTANCE --zone=ZONE \
  --machine-type=e2-standard-4
gcloud compute instances start INSTANCE --zone=ZONE
```

### SSH and SCP

```bash
# SSH into an instance
gcloud compute ssh INSTANCE --zone=ZONE
gcloud compute ssh INSTANCE --zone=ZONE --command="uptime"
gcloud compute ssh INSTANCE --zone=ZONE --tunnel-through-iap  # IAP tunnel

# SCP files
gcloud compute scp LOCAL_FILE INSTANCE:~/REMOTE_PATH --zone=ZONE
gcloud compute scp INSTANCE:~/REMOTE_FILE ./LOCAL_PATH --zone=ZONE
gcloud compute scp --recurse LOCAL_DIR INSTANCE:~/REMOTE_DIR --zone=ZONE
```

## Disks

```bash
# Create a persistent disk
gcloud compute disks create DISK_NAME \
  --zone=ZONE --size=100GB --type=pd-ssd

# List disks
gcloud compute disks list

# Attach to an instance
gcloud compute instances attach-disk INSTANCE --disk=DISK_NAME --zone=ZONE

# Detach
gcloud compute instances detach-disk INSTANCE --disk=DISK_NAME --zone=ZONE

# Create snapshot
gcloud compute disks snapshot DISK_NAME --zone=ZONE --snapshot-names=SNAPSHOT_NAME

# List snapshots
gcloud compute snapshots list

# Create disk from snapshot
gcloud compute disks create NEW_DISK --source-snapshot=SNAPSHOT_NAME --zone=ZONE

# Delete
gcloud compute disks delete DISK_NAME --zone=ZONE
```

## Images

```bash
# List available images
gcloud compute images list
gcloud compute images list --filter="family:debian"

# Create custom image from disk
gcloud compute images create IMAGE_NAME --source-disk=DISK --source-disk-zone=ZONE

# Create from instance (must stop first)
gcloud compute images create IMAGE_NAME --source-disk=INSTANCE --source-disk-zone=ZONE

# Delete
gcloud compute images delete IMAGE_NAME
```

## Networking

### VPC networks

```bash
# Create a VPC
gcloud compute networks create NETWORK_NAME --subnet-mode=auto
gcloud compute networks create NETWORK_NAME --subnet-mode=custom

# Create a subnet
gcloud compute networks subnets create SUBNET_NAME \
  --network=NETWORK --region=REGION --range=10.0.0.0/24

# List networks and subnets
gcloud compute networks list
gcloud compute networks subnets list
```

### Firewall rules

```bash
# Create a firewall rule
gcloud compute firewall-rules create RULE_NAME \
  --network=NETWORK \
  --allow=tcp:80,tcp:443 \
  --source-ranges=0.0.0.0/0 \
  --target-tags=web-server

# Allow SSH
gcloud compute firewall-rules create allow-ssh \
  --network=default \
  --allow=tcp:22 \
  --source-ranges=0.0.0.0/0

# Allow internal traffic
gcloud compute firewall-rules create allow-internal \
  --network=NETWORK \
  --allow=tcp,udp,icmp \
  --source-ranges=10.0.0.0/8

# List firewall rules
gcloud compute firewall-rules list
gcloud compute firewall-rules list --filter="network:default"

# Delete
gcloud compute firewall-rules delete RULE_NAME
```

### Static IPs

```bash
# Reserve external IP
gcloud compute addresses create IP_NAME --region=REGION

# Reserve global IP (for load balancers)
gcloud compute addresses create IP_NAME --global

# List addresses
gcloud compute addresses list

# Describe (get the IP)
gcloud compute addresses describe IP_NAME --region=REGION \
  --format="value(address)"
```

## Instance groups and autoscaling

```bash
# Create instance template
gcloud compute instance-templates create TEMPLATE_NAME \
  --machine-type=e2-medium \
  --image-family=debian-12 --image-project=debian-cloud

# Create managed instance group
gcloud compute instance-groups managed create GROUP_NAME \
  --template=TEMPLATE_NAME --size=3 --zone=ZONE

# Set autoscaling
gcloud compute instance-groups managed set-autoscaling GROUP_NAME \
  --zone=ZONE \
  --min-num-replicas=1 --max-num-replicas=10 \
  --target-cpu-utilization=0.6
```

## Troubleshooting

- **"Zone not found"** — verify zone exists with `gcloud compute zones list`
- **Cannot SSH** — check firewall rules allow tcp:22; try `--tunnel-through-iap` for VMs without external IP
- **"Quota exceeded"** — check quotas with `gcloud compute project-info describe` or in Cloud Console
- **Instance won't start** — check `gcloud compute instances get-serial-port-output INSTANCE --zone=ZONE` for boot errors
- **Network connectivity** — verify firewall rules, network tags, and routes with `gcloud compute firewall-rules list`
