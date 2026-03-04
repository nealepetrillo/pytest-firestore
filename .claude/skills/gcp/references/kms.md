# gcloud kms — Cloud KMS (Key Management Service) Reference

## Contents
- [Overview](#overview)
- [Key rings](#key-rings)
- [Keys](#keys)
- [Key versions](#key-versions)
- [Encrypt and decrypt](#encrypt-and-decrypt)
- [Sign and verify](#sign-and-verify)
- [IAM](#iam)
- [CMEK (Customer-Managed Encryption Keys)](#cmek-customer-managed-encryption-keys)
- [Troubleshooting](#troubleshooting)

## Overview

Cloud KMS manages cryptographic keys for encrypting data, signing payloads, and managing secrets. Keys are organized in key rings, and key rings belong to a location. Key material never leaves Google's infrastructure.

## Key rings

```bash
# Create a key ring
gcloud kms keyrings create KEYRING_NAME --location=LOCATION

# List key rings
gcloud kms keyrings list --location=LOCATION
gcloud kms keyrings list --location=global

# Describe
gcloud kms keyrings describe KEYRING_NAME --location=LOCATION
```

Key rings cannot be deleted once created.

## Keys

### Create

```bash
# Symmetric encryption key (default, most common)
gcloud kms keys create KEY_NAME \
  --keyring=KEYRING --location=LOCATION \
  --purpose=encryption

# Asymmetric encryption key
gcloud kms keys create KEY_NAME \
  --keyring=KEYRING --location=LOCATION \
  --purpose=asymmetric-encryption \
  --default-algorithm=rsa-decrypt-oaep-4096-sha256

# Asymmetric signing key
gcloud kms keys create KEY_NAME \
  --keyring=KEYRING --location=LOCATION \
  --purpose=asymmetric-signing \
  --default-algorithm=ec-sign-p256-sha256

# MAC signing key
gcloud kms keys create KEY_NAME \
  --keyring=KEYRING --location=LOCATION \
  --purpose=mac \
  --default-algorithm=hmac-sha256

# With rotation schedule (symmetric only)
gcloud kms keys create KEY_NAME \
  --keyring=KEYRING --location=LOCATION \
  --purpose=encryption \
  --rotation-period=90d \
  --next-rotation-time=2025-07-01T00:00:00Z

# With custom protection level (HSM)
gcloud kms keys create KEY_NAME \
  --keyring=KEYRING --location=LOCATION \
  --purpose=encryption \
  --protection-level=hsm
```

### Manage

```bash
# List keys
gcloud kms keys list --keyring=KEYRING --location=LOCATION

# Describe
gcloud kms keys describe KEY_NAME \
  --keyring=KEYRING --location=LOCATION

# Update rotation schedule
gcloud kms keys update KEY_NAME \
  --keyring=KEYRING --location=LOCATION \
  --rotation-period=60d \
  --next-rotation-time=2025-08-01T00:00:00Z

# Remove rotation schedule
gcloud kms keys update KEY_NAME \
  --keyring=KEYRING --location=LOCATION \
  --remove-rotation-schedule
```

## Key versions

```bash
# List versions
gcloud kms keys versions list \
  --key=KEY_NAME --keyring=KEYRING --location=LOCATION

# Describe a version
gcloud kms keys versions describe VERSION \
  --key=KEY_NAME --keyring=KEYRING --location=LOCATION

# Disable a version
gcloud kms keys versions disable VERSION \
  --key=KEY_NAME --keyring=KEYRING --location=LOCATION

# Enable a version
gcloud kms keys versions enable VERSION \
  --key=KEY_NAME --keyring=KEYRING --location=LOCATION

# Schedule destruction (default 24h waiting period)
gcloud kms keys versions destroy VERSION \
  --key=KEY_NAME --keyring=KEYRING --location=LOCATION

# Restore a version scheduled for destruction
gcloud kms keys versions restore VERSION \
  --key=KEY_NAME --keyring=KEYRING --location=LOCATION

# Get public key (asymmetric keys only)
gcloud kms keys versions get-public-key VERSION \
  --key=KEY_NAME --keyring=KEYRING --location=LOCATION \
  --output-file=public_key.pem
```

## Encrypt and decrypt

```bash
# Encrypt data (symmetric)
gcloud kms encrypt \
  --key=KEY_NAME --keyring=KEYRING --location=LOCATION \
  --plaintext-file=plaintext.txt \
  --ciphertext-file=ciphertext.enc

# Decrypt data
gcloud kms decrypt \
  --key=KEY_NAME --keyring=KEYRING --location=LOCATION \
  --ciphertext-file=ciphertext.enc \
  --plaintext-file=decrypted.txt

# Encrypt with additional authenticated data (AAD)
gcloud kms encrypt \
  --key=KEY_NAME --keyring=KEYRING --location=LOCATION \
  --plaintext-file=plaintext.txt \
  --ciphertext-file=ciphertext.enc \
  --additional-authenticated-data-file=aad.txt

# Asymmetric encrypt
gcloud kms asymmetric-encrypt \
  --key=KEY_NAME --keyring=KEYRING --location=LOCATION \
  --version=VERSION \
  --plaintext-file=plaintext.txt \
  --ciphertext-file=ciphertext.enc

# Asymmetric decrypt
gcloud kms asymmetric-decrypt \
  --key=KEY_NAME --keyring=KEYRING --location=LOCATION \
  --version=VERSION \
  --ciphertext-file=ciphertext.enc \
  --plaintext-file=decrypted.txt
```

## Sign and verify

```bash
# Asymmetric sign
gcloud kms asymmetric-sign \
  --key=KEY_NAME --keyring=KEYRING --location=LOCATION \
  --version=VERSION \
  --input-file=data.txt \
  --signature-file=signature.sig

# MAC sign
gcloud kms mac-sign \
  --key=KEY_NAME --keyring=KEYRING --location=LOCATION \
  --version=VERSION \
  --input-file=data.txt \
  --signature-file=mac.sig

# MAC verify
gcloud kms mac-verify \
  --key=KEY_NAME --keyring=KEYRING --location=LOCATION \
  --version=VERSION \
  --input-file=data.txt \
  --signature-file=mac.sig
```

## IAM

```bash
# Grant encrypt/decrypt permission
gcloud kms keys add-iam-policy-binding KEY_NAME \
  --keyring=KEYRING --location=LOCATION \
  --member="serviceAccount:SA_EMAIL" \
  --role="roles/cloudkms.cryptoKeyEncrypterDecrypter"

# Grant encrypt-only
gcloud kms keys add-iam-policy-binding KEY_NAME \
  --keyring=KEYRING --location=LOCATION \
  --member="serviceAccount:SA_EMAIL" \
  --role="roles/cloudkms.cryptoKeyEncrypter"

# View policy
gcloud kms keys get-iam-policy KEY_NAME \
  --keyring=KEYRING --location=LOCATION
```

## CMEK (Customer-Managed Encryption Keys)

Use KMS keys to encrypt GCP resources:

```bash
# Cloud Storage
gcloud storage buckets update gs://BUCKET \
  --default-encryption-key=projects/PROJECT/locations/LOCATION/keyRings/KEYRING/cryptoKeys/KEY

# BigQuery
bq mk --table --encryption_kms_key=projects/PROJECT/locations/LOCATION/keyRings/KEYRING/cryptoKeys/KEY \
  DATASET.TABLE SCHEMA

# Compute Engine disk
gcloud compute disks create DISK \
  --zone=ZONE \
  --kms-key=projects/PROJECT/locations/LOCATION/keyRings/KEYRING/cryptoKeys/KEY
```

## Troubleshooting

- **"Key ring cannot be deleted"** — key rings are permanent; disable or destroy key versions instead
- **"Permission denied"** — ensure the caller has the appropriate KMS role on the key
- **"Key version is disabled/destroyed"** — check version state; restore if scheduled for destruction
- **CMEK errors** — the GCP service agent must have `roles/cloudkms.cryptoKeyEncrypterDecrypter` on the key
- **Key rotation** — rotation creates a new version; old versions remain usable for decryption
