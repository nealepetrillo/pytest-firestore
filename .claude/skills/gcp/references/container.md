# gcloud container — Google Kubernetes Engine (GKE) Reference

## Contents
- [Overview](#overview)
- [Clusters](#clusters)
- [Node pools](#node-pools)
- [Kubectl integration](#kubectl-integration)
- [Operations](#operations)
- [Common patterns](#common-patterns)
- [Troubleshooting](#troubleshooting)

## Overview

`gcloud container` manages GKE clusters, node pools, and related resources. GKE runs Kubernetes on GCP with managed control planes, auto-upgrades, and tight integration with GCP services.

## Clusters

### Create

```bash
# Autopilot cluster (recommended — Google manages node infrastructure)
gcloud container clusters create-auto CLUSTER_NAME \
  --region=REGION \
  --project=PROJECT_ID

# Standard cluster (you manage node pools)
gcloud container clusters create CLUSTER_NAME \
  --region=REGION \
  --num-nodes=3 \
  --machine-type=e2-standard-4 \
  --enable-autoscaling --min-nodes=1 --max-nodes=10

# Zonal cluster (single zone, cheaper for dev)
gcloud container clusters create CLUSTER_NAME \
  --zone=ZONE \
  --num-nodes=3

# With Workload Identity
gcloud container clusters create CLUSTER_NAME \
  --region=REGION \
  --workload-pool=PROJECT_ID.svc.id.goog

# Private cluster (no public IPs on nodes)
gcloud container clusters create CLUSTER_NAME \
  --region=REGION \
  --enable-private-nodes \
  --master-ipv4-cidr=172.16.0.0/28 \
  --enable-ip-alias
```

**Common flags:**
- `--region` / `--zone` — regional (HA) vs zonal cluster
- `--num-nodes` — nodes per zone
- `--machine-type` — node machine type
- `--disk-size` — node boot disk size
- `--disk-type` — `pd-standard`, `pd-ssd`, `pd-balanced`
- `--enable-autoscaling` — enable cluster autoscaler
- `--min-nodes` / `--max-nodes` — autoscaler bounds
- `--enable-ip-alias` — VPC-native cluster (recommended)
- `--network` / `--subnetwork` — VPC placement
- `--release-channel` — `rapid`, `regular`, `stable`
- `--cluster-version` — specific Kubernetes version
- `--service-account` — node service account

### Manage clusters

```bash
# List clusters
gcloud container clusters list
gcloud container clusters list --format="table(name,location,currentMasterVersion,status)"

# Describe
gcloud container clusters describe CLUSTER --region=REGION

# Get credentials (configures kubectl)
gcloud container clusters get-credentials CLUSTER --region=REGION
gcloud container clusters get-credentials CLUSTER --zone=ZONE

# Update cluster settings
gcloud container clusters update CLUSTER --region=REGION \
  --enable-autoscaling --min-nodes=2 --max-nodes=20

# Upgrade cluster master
gcloud container clusters upgrade CLUSTER --region=REGION --master

# Resize (standard clusters)
gcloud container clusters resize CLUSTER --region=REGION \
  --num-nodes=5 --node-pool=default-pool

# Delete
gcloud container clusters delete CLUSTER --region=REGION
```

## Node pools

```bash
# Create a node pool
gcloud container node-pools create POOL_NAME \
  --cluster=CLUSTER --region=REGION \
  --machine-type=n2-standard-8 \
  --num-nodes=3 \
  --enable-autoscaling --min-nodes=0 --max-nodes=10

# GPU node pool
gcloud container node-pools create gpu-pool \
  --cluster=CLUSTER --region=REGION \
  --machine-type=n1-standard-4 \
  --accelerator=type=nvidia-tesla-t4,count=1 \
  --num-nodes=1

# Spot node pool (preemptible, much cheaper)
gcloud container node-pools create spot-pool \
  --cluster=CLUSTER --region=REGION \
  --spot --machine-type=e2-standard-4 \
  --num-nodes=3

# List node pools
gcloud container node-pools list --cluster=CLUSTER --region=REGION

# Describe
gcloud container node-pools describe POOL --cluster=CLUSTER --region=REGION

# Update
gcloud container node-pools update POOL --cluster=CLUSTER --region=REGION \
  --enable-autoscaling --min-nodes=1 --max-nodes=20

# Delete
gcloud container node-pools delete POOL --cluster=CLUSTER --region=REGION
```

## Kubectl integration

```bash
# Get credentials (sets kubectl context)
gcloud container clusters get-credentials CLUSTER --region=REGION

# Verify connection
kubectl cluster-info
kubectl get nodes

# Switch between cluster contexts
kubectl config get-contexts
kubectl config use-context CONTEXT_NAME
```

## Operations

```bash
# List cluster operations (upgrades, repairs, etc.)
gcloud container operations list --region=REGION

# Describe an operation
gcloud container operations describe OPERATION_ID --region=REGION

# Wait for an operation
gcloud container operations wait OPERATION_ID --region=REGION
```

## Common patterns

### Deploy an application

```bash
gcloud container clusters get-credentials CLUSTER --region=REGION
kubectl create deployment my-app --image=IMAGE_URL
kubectl expose deployment my-app --type=LoadBalancer --port=80 --target-port=8080
```

### Set up Workload Identity

```bash
# 1. Enable on cluster
gcloud container clusters update CLUSTER --region=REGION \
  --workload-pool=PROJECT_ID.svc.id.goog

# 2. Create GCP service account
gcloud iam service-accounts create GSA_NAME

# 3. Grant GCP roles to the GSA
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:GSA_NAME@PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/ROLE"

# 4. Bind KSA to GSA
gcloud iam service-accounts add-iam-policy-binding \
  GSA_NAME@PROJECT_ID.iam.gserviceaccount.com \
  --role="roles/iam.workloadIdentityUser" \
  --member="serviceAccount:PROJECT_ID.svc.id.goog[NAMESPACE/KSA_NAME]"

# 5. Annotate KSA
kubectl annotate serviceaccount KSA_NAME \
  --namespace=NAMESPACE \
  iam.gke.io/gcp-service-account=GSA_NAME@PROJECT_ID.iam.gserviceaccount.com
```

## Troubleshooting

- **"Unable to connect to the server"** — re-run `get-credentials`; check cluster status with `gcloud container clusters list`
- **Nodes not scaling** — verify autoscaler is enabled; check `kubectl describe nodes` for resource pressure
- **Pod scheduling failures** — check `kubectl describe pod POD` for events; may need more nodes or different machine type
- **"Workload Identity not enabled"** — ensure `--workload-pool` is set on the cluster
- **Upgrade issues** — check release notes for your channel; use `gcloud container get-server-config --region=REGION` to see available versions
