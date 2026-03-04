# gcloud functions & gcloud run — Serverless Compute Reference

Cloud Functions (Gen2) runs on Cloud Run under the hood. Many operational commands (logs, revisions, traffic splitting) use `gcloud run` even for Gen2 functions.

## Contents
- [Cloud Functions](#cloud-functions)
- [Cloud Run](#cloud-run)
- [Relationship: Cloud Functions Gen2 ↔ Cloud Run](#relationship-cloud-functions-gen2--cloud-run)
- [Troubleshooting](#troubleshooting)

## Cloud Functions

### gcloud functions deploy

```bash
gcloud functions deploy FUNCTION_NAME \
  --gen2 \
  --runtime=RUNTIME \
  --region=REGION \
  --source=SOURCE \
  --entry-point=ENTRY_POINT \
  TRIGGER_FLAGS \
  [OPTIONAL_FLAGS]
```

**Required flags:**
- `--gen2` — use 2nd gen runtime (recommended; set default with `gcloud config set functions/gen2 true`)
- `--runtime` — e.g. `python312`, `python311`, `nodejs20`, `go122`, `java21`, `ruby33`, `dotnet8`
- `--region` — required for Gen2 (e.g. `us-central1`)
- `--source` — path to source (`.` for current dir, GCS URI, or repo URL)
- `--entry-point` — function name in source code

**Trigger flags (pick one):**
- `--trigger-http` — HTTP endpoint
- `--trigger-topic=TOPIC` — Pub/Sub topic
- `--trigger-bucket=BUCKET` — Cloud Storage bucket (Gen1 only)
- `--trigger-event-filters="type=EVENT_TYPE"` — Eventarc trigger (Gen2)
  - GCS example: `--trigger-event-filters="type=google.cloud.storage.object.v1.finalized" --trigger-event-filters="bucket=MY_BUCKET"`
  - Audit log: `--trigger-event-filters="type=google.cloud.audit.log.v1.written" --trigger-event-filters="serviceName=storage.googleapis.com"`

**Common optional flags:**
- `--allow-unauthenticated` / `--no-allow-unauthenticated` — public access
- `--service-account=SA_EMAIL` — runtime service account (Gen1)
- `--run-service-account=SA_EMAIL` — runtime service account (Gen2)
- `--set-env-vars=KEY1=VAL1,KEY2=VAL2` — environment variables
- `--update-env-vars=KEY=VAL` — add/update without clearing others
- `--set-secrets=ENV_VAR=SECRET:VERSION` — Secret Manager integration
- `--memory=MEMORY` — e.g. `256MB`, `512MB`, `1GB`, `2GB` (up to `32GB` Gen2)
- `--cpu=CPU` — Gen2 only, e.g. `1`, `2`, `4`
- `--timeout=DURATION` — max execution time, e.g. `60s`, `540s` (Gen1 max), `3600s` (Gen2 max)
- `--min-instances=N` — keep warm instances to avoid cold starts
- `--max-instances=N` — concurrency cap
- `--concurrency=N` — Gen2 only, requests per instance (default 1, max 1000)
- `--vpc-connector=CONNECTOR` — Serverless VPC Access connector
- `--egress-settings=SETTING` — `all`, `all-traffic`, `private-ranges-only`
- `--ingress-settings=SETTING` — `all`, `internal-only`, `internal-and-gclb`
- `--retry` — retry on failure (event-triggered functions)
- `--docker-registry=REGISTRY` — `artifact-registry` (default for Gen2)

**Gen2 function names** must comply with RFC 1123: lowercase letters, numbers, hyphens only. Max 63 chars.

### Other function commands

```bash
# List functions
gcloud functions list --region=REGION
gcloud functions list --gen2 --region=REGION

# Describe a function
gcloud functions describe FUNCTION_NAME --region=REGION --gen2

# Get the URL of an HTTP function
gcloud functions describe FUNCTION_NAME --region=REGION --gen2 \
  --format="value(serviceConfig.uri)"

# Call a function directly (testing)
gcloud functions call FUNCTION_NAME --region=REGION --gen2 \
  --data='{"key":"value"}'

# View logs
gcloud functions logs read FUNCTION_NAME --region=REGION --gen2 --limit=50

# Delete a function
gcloud functions delete FUNCTION_NAME --region=REGION --gen2

# List runtimes
gcloud functions runtimes list --region=REGION
```

### Required APIs

Enable before first deployment:
```bash
gcloud services enable \
  cloudfunctions.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  run.googleapis.com \
  eventarc.googleapis.com \
  logging.googleapis.com
```

## Cloud Run

### gcloud run deploy

```bash
gcloud run deploy SERVICE_NAME \
  --image=IMAGE_URL \
  --region=REGION \
  [OPTIONAL_FLAGS]
```

**Deploy from source (builds automatically via Cloud Build):**
```bash
gcloud run deploy SERVICE_NAME --source=. --region=REGION
```

**Common flags:**
- `--image=IMAGE_URL` — container image (e.g. `gcr.io/PROJECT/IMAGE:TAG` or Artifact Registry URL)
- `--source=.` — deploy from source (auto-builds with Buildpacks or Dockerfile)
- `--allow-unauthenticated` / `--no-allow-unauthenticated`
- `--service-account=SA_EMAIL`
- `--set-env-vars=KEY=VAL` / `--update-env-vars=KEY=VAL`
- `--set-secrets=ENV_VAR=SECRET:VERSION`
- `--memory=MEMORY` — e.g. `512Mi`, `1Gi`, `2Gi`
- `--cpu=CPU` — e.g. `1`, `2`, `4`, `8`
- `--timeout=DURATION` — request timeout, e.g. `300s` (max 3600s)
- `--min-instances=N` / `--max-instances=N`
- `--concurrency=N` — max concurrent requests per instance
- `--port=PORT` — container port (default 8080)
- `--vpc-connector=CONNECTOR` / `--vpc-egress=SETTING`
- `--ingress=SETTING` — `all`, `internal`, `internal-and-cloud-load-balancing`
- `--no-traffic` — deploy without routing traffic (for gradual rollouts)
- `--tag=TAG` — assign a traffic tag for direct URL testing
- `--revision-suffix=SUFFIX` — custom revision name suffix
- `--cpu-boost` — temporarily boost CPU on startup
- `--session-affinity` — route requests from same client to same instance

### Services management

```bash
# List services
gcloud run services list --region=REGION
gcloud run services list --format="table(metadata.name,status.url)"

# Describe a service
gcloud run services describe SERVICE --region=REGION

# Update a service (without redeploying)
gcloud run services update SERVICE --region=REGION \
  --update-env-vars=KEY=NEW_VAL \
  --memory=1Gi

# Delete a service
gcloud run services delete SERVICE --region=REGION

# Get service URL
gcloud run services describe SERVICE --region=REGION \
  --format="value(status.url)"
```

### Revisions and traffic

```bash
# List revisions
gcloud run revisions list --service=SERVICE --region=REGION

# Describe a revision
gcloud run revisions describe REVISION --region=REGION

# Delete old revision
gcloud run revisions delete REVISION --region=REGION

# Split traffic between revisions
gcloud run services update-traffic SERVICE --region=REGION \
  --to-revisions=REV1=70,REV2=30

# Route 100% to latest
gcloud run services update-traffic SERVICE --region=REGION \
  --to-latest

# Route traffic by tag
gcloud run services update-traffic SERVICE --region=REGION \
  --to-tags=TAG_NAME=PERCENT
```

### Cloud Run Jobs

Jobs run to completion (batch processing, migrations, scheduled tasks).

```bash
# Create a job
gcloud run jobs create JOB_NAME \
  --image=IMAGE_URL \
  --region=REGION \
  --tasks=N \
  --max-retries=RETRIES \
  --task-timeout=DURATION

# Execute a job
gcloud run jobs execute JOB_NAME --region=REGION

# Execute and wait for completion
gcloud run jobs execute JOB_NAME --region=REGION --wait

# List jobs
gcloud run jobs list --region=REGION

# Describe a job
gcloud run jobs describe JOB_NAME --region=REGION

# Update a job
gcloud run jobs update JOB_NAME --region=REGION --update-env-vars=KEY=VAL

# Delete a job
gcloud run jobs delete JOB_NAME --region=REGION
```

### IAM for Cloud Run

```bash
# Make a service publicly accessible
gcloud run services add-iam-policy-binding SERVICE --region=REGION \
  --member="allUsers" --role="roles/run.invoker"

# Grant invoke access to a specific account
gcloud run services add-iam-policy-binding SERVICE --region=REGION \
  --member="serviceAccount:SA@PROJECT.iam.gserviceaccount.com" \
  --role="roles/run.invoker"

# View IAM policy
gcloud run services get-iam-policy SERVICE --region=REGION
```

### Authenticated invocation

```bash
# Get an identity token and curl a private service
TOKEN=$(gcloud auth print-identity-token)
curl -H "Authorization: Bearer $TOKEN" $(gcloud run services describe SERVICE \
  --region=REGION --format="value(status.url)")
```

## Relationship: Cloud Functions Gen2 ↔ Cloud Run

Gen2 functions are Cloud Run services under the hood. This means:
- Deployed functions appear in `gcloud run services list`
- Revision and traffic management use `gcloud run` commands
- Logs appear in both `gcloud functions logs` and Cloud Logging
- Concurrency, min/max instances, and VPC settings behave identically
- Function names must be RFC 1123 compliant (lowercase, hyphens, max 63 chars)

## Troubleshooting

- **"API not enabled"** — run `gcloud services enable` for required APIs
- **"Could not create Cloud Run service"** — function name likely violates RFC 1123
- **Cold starts** — set `--min-instances=1` to keep at least one instance warm
- **Timeout errors** — Gen1 max is 540s, Gen2/Cloud Run max is 3600s
- **Permission denied on invoke** — check IAM; for private services use `--no-allow-unauthenticated` and grant `roles/run.invoker`
- **View build logs** — `gcloud builds list` and `gcloud builds log BUILD_ID`
