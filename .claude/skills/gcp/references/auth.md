# gcloud auth — Authentication & Credentials Reference

## Contents
- [Critical Concept: gcloud Auth vs ADC](#critical-concept-gcloud-auth-vs-adc)
- [Subcommands](#subcommands)
- [Service Account Impersonation](#service-account-impersonation)
- [Access Token from File](#access-token-from-file)
- [ADC Credential Resolution Order](#adc-credential-resolution-order)
- [Common Patterns](#common-patterns)

## Critical Concept: gcloud Auth vs ADC

These are **two separate credential stores** that serve different purposes:

| Aspect | gcloud CLI credentials | Application Default Credentials (ADC) |
|--------|----------------------|---------------------------------------|
| Set by | `gcloud auth login` | `gcloud auth application-default login` |
| Used by | `gcloud` commands | Client libraries, application code |
| Stored at | `~/.config/gcloud/` | `~/.config/gcloud/application_default_credentials.json` |
| Env override | N/A | `GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json` |

They can use the same or different accounts. Logging into one does NOT configure the other.

## Subcommands

### gcloud auth login
Authorize gcloud CLI with user credentials via browser-based OAuth flow.

```bash
gcloud auth login                          # Interactive browser flow
gcloud auth login --no-launch-browser      # Headless — prints URL to open elsewhere
gcloud auth login --no-browser             # Remote bootstrap — copy command to machine with browser
gcloud auth login --cred-file=PATH         # Use external credential config (Workload Identity Federation)
gcloud auth login ACCOUNT                  # Login specific account
```

Key flags:
- `--no-launch-browser` — for SSH sessions without browser access; prints URL to paste
- `--no-browser` — for machines without gcloud on a browser-equipped machine; uses remote bootstrap
- `--activate` — set as active account (default behavior)
- `--update-adc` — also update Application Default Credentials
- `--enable-gdrive-access` — request Google Drive read-only scope
- `--login-config=PATH` — Workforce Identity Federation login config file

### gcloud auth activate-service-account
Authorize with a service account key file (non-interactive).

```bash
gcloud auth activate-service-account SA_EMAIL --key-file=KEY.json
gcloud auth activate-service-account --key-file=KEY.json   # email inferred from key
```

### gcloud auth application-default login
Configure ADC with user credentials for local development.

```bash
gcloud auth application-default login
gcloud auth application-default login --scopes=SCOPE1,SCOPE2
gcloud auth application-default login --client-id-file=CLIENT_ID.json
```

This writes credentials to `~/.config/gcloud/application_default_credentials.json`. Client libraries automatically use this file when `GOOGLE_APPLICATION_CREDENTIALS` is not set.

### gcloud auth application-default set-quota-project
Set the billing/quota project for ADC.

```bash
gcloud auth application-default set-quota-project PROJECT_ID
```

Required when your account lacks `serviceusage.services.use` permission on the target project.

### gcloud auth application-default revoke
Revoke ADC credentials.

```bash
gcloud auth application-default revoke
```

### gcloud auth application-default print-access-token
Print an OAuth2 access token from the current ADC. Useful for manual API testing with curl.

```bash
TOKEN=$(gcloud auth application-default print-access-token)
curl -H "Authorization: Bearer $TOKEN" https://www.googleapis.com/...
```

### gcloud auth print-access-token
Print an access token for the active gcloud CLI account (not ADC).

```bash
TOKEN=$(gcloud auth print-access-token)
curl -H "Authorization: Bearer $TOKEN" https://www.googleapis.com/...

# For a specific account:
gcloud auth print-access-token ACCOUNT
# With impersonation:
gcloud auth print-access-token --impersonate-service-account=SA_EMAIL
```

### gcloud auth print-identity-token
Print an OIDC identity token for the active account. Used for authenticating to Cloud Run, Cloud Functions, and IAP-protected resources.

```bash
gcloud auth print-identity-token
gcloud auth print-identity-token --audiences=URL
gcloud auth print-identity-token --impersonate-service-account=SA_EMAIL --audiences=URL
```

### gcloud auth list
List all credentialed accounts.

```bash
gcloud auth list
gcloud auth list --format="value(account)"    # Just email addresses
gcloud auth list --filter-account=ACCOUNT      # Check specific account
```

### gcloud auth describe
Show details about a specific credential.

```bash
gcloud auth describe ACCOUNT
```

### gcloud auth revoke
Revoke credentials for an account.

```bash
gcloud auth revoke                    # Revoke active account
gcloud auth revoke ACCOUNT            # Revoke specific account
gcloud auth revoke --all              # Revoke all accounts
```

### gcloud auth configure-docker
Register gcloud as a Docker credential helper for pushing/pulling container images.

```bash
gcloud auth configure-docker                              # Default: gcr.io
gcloud auth configure-docker REGION-docker.pkg.dev        # Artifact Registry
gcloud auth configure-docker us-central1-docker.pkg.dev,us-east1-docker.pkg.dev
```

This modifies `~/.docker/config.json` to add gcloud as a credHelper.

### gcloud auth git-helper
Git credential helper for Cloud Source Repositories. Typically configured automatically.

## Service Account Impersonation

Instead of downloading key files, impersonate a service account:

```bash
# Per-command:
gcloud COMMAND --impersonate-service-account=SA_EMAIL

# Set as default for all commands:
gcloud config set auth/impersonate_service_account SA_EMAIL

# Stop impersonating:
gcloud config unset auth/impersonate_service_account
```

Requirements: the calling account needs `roles/iam.serviceAccountTokenCreator` on the target SA.

## Access Token from File

```bash
gcloud COMMAND --access-token-file=/path/to/token
# Or via env var:
export CLOUDSDK_AUTH_ACCESS_TOKEN="ya29...."
```

## ADC Credential Resolution Order

When application code calls Google Cloud client libraries, ADC checks in this order:
1. `GOOGLE_APPLICATION_CREDENTIALS` environment variable (path to JSON key file)
2. User credentials from `gcloud auth application-default login`
3. Attached service account (on GCE, Cloud Run, Cloud Functions, GKE, etc.)
4. Metadata server (on Google Cloud compute environments)

## Common Patterns

### Local development setup
```bash
gcloud auth login                          # For gcloud CLI
gcloud auth application-default login      # For application code
gcloud config set project MY_PROJECT
```

### CI/CD with service account
```bash
gcloud auth activate-service-account --key-file=$GOOGLE_CREDENTIALS
gcloud config set project $GCP_PROJECT
```

### Debugging auth issues
```bash
gcloud auth list                           # Which accounts are credentialed?
gcloud config list                         # Which project/account is active?
gcloud info                                # Full environment info
echo $GOOGLE_APPLICATION_CREDENTIALS       # ADC override set?
gcloud auth application-default print-access-token  # Does ADC work?
```
