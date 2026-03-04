# gcloud dns — Cloud DNS Reference

## Contents
- [Overview](#overview)
- [Managed zones](#managed-zones)
- [Record sets](#record-sets)
- [Common record types](#common-record-types)
- [DNS policies](#dns-policies)
- [DNSSEC](#dnssec)
- [Troubleshooting](#troubleshooting)

## Overview

Cloud DNS is a scalable, reliable DNS service. It manages DNS zones (public and private) and record sets. DNS changes are transactional.

## Managed zones

```bash
# Create a public zone
gcloud dns managed-zones create ZONE_NAME \
  --dns-name="example.com." \
  --description="Production DNS zone"

# Create a private zone (accessible only within specified VPCs)
gcloud dns managed-zones create ZONE_NAME \
  --dns-name="internal.example.com." \
  --description="Private DNS" \
  --visibility=private \
  --networks=VPC_NETWORK_URL

# Create with DNSSEC enabled
gcloud dns managed-zones create ZONE_NAME \
  --dns-name="example.com." \
  --dnssec-state=on

# List zones
gcloud dns managed-zones list

# Describe
gcloud dns managed-zones describe ZONE_NAME

# Update
gcloud dns managed-zones update ZONE_NAME --description="New description"

# Delete (must remove all non-default records first)
gcloud dns managed-zones delete ZONE_NAME
```

## Record sets

### Transaction-based changes

```bash
# Start a transaction
gcloud dns record-sets transaction start --zone=ZONE_NAME

# Add a record
gcloud dns record-sets transaction add "1.2.3.4" \
  --zone=ZONE_NAME \
  --name="www.example.com." \
  --type=A \
  --ttl=300

# Add multiple values (e.g., MX records)
gcloud dns record-sets transaction add "10 mail1.example.com." "20 mail2.example.com." \
  --zone=ZONE_NAME \
  --name="example.com." \
  --type=MX \
  --ttl=3600

# Remove a record
gcloud dns record-sets transaction remove "1.2.3.4" \
  --zone=ZONE_NAME \
  --name="www.example.com." \
  --type=A \
  --ttl=300

# Execute the transaction
gcloud dns record-sets transaction execute --zone=ZONE_NAME

# Abort (discard pending changes)
gcloud dns record-sets transaction abort --zone=ZONE_NAME
```

### Direct record management

```bash
# Create a record directly
gcloud dns record-sets create www.example.com. \
  --zone=ZONE_NAME \
  --type=A \
  --rrdatas="1.2.3.4" \
  --ttl=300

# CNAME record
gcloud dns record-sets create app.example.com. \
  --zone=ZONE_NAME \
  --type=CNAME \
  --rrdatas="my-service.run.app." \
  --ttl=300

# TXT record
gcloud dns record-sets create example.com. \
  --zone=ZONE_NAME \
  --type=TXT \
  --rrdatas='"v=spf1 include:_spf.google.com ~all"' \
  --ttl=3600

# Update a record
gcloud dns record-sets update www.example.com. \
  --zone=ZONE_NAME \
  --type=A \
  --rrdatas="5.6.7.8" \
  --ttl=300

# Delete a record
gcloud dns record-sets delete www.example.com. \
  --zone=ZONE_NAME \
  --type=A
```

### List and describe

```bash
# List all records in a zone
gcloud dns record-sets list --zone=ZONE_NAME
gcloud dns record-sets list --zone=ZONE_NAME \
  --format="table(name,type,ttl,rrdatas)"

# Filter by type
gcloud dns record-sets list --zone=ZONE_NAME --filter="type=A"

# Describe a specific record
gcloud dns record-sets describe www.example.com. \
  --zone=ZONE_NAME --type=A
```

## Common record types

| Type | Purpose | Example |
|------|---------|---------|
| `A` | IPv4 address | `1.2.3.4` |
| `AAAA` | IPv6 address | `2001:db8::1` |
| `CNAME` | Canonical name (alias) | `alias.example.com.` |
| `MX` | Mail exchange | `10 mail.example.com.` |
| `TXT` | Text (SPF, DKIM, verification) | `"v=spf1 ..."` |
| `NS` | Name server | `ns1.example.com.` |
| `SRV` | Service locator | `10 5 5060 sip.example.com.` |
| `CAA` | Certificate authority auth | `0 issue "letsencrypt.org"` |

## DNS policies

```bash
# Create a DNS policy (e.g., enable logging)
gcloud dns policies create POLICY_NAME \
  --networks=VPC_NETWORK \
  --enable-logging

# Enable inbound DNS forwarding (allow on-prem to resolve private zones)
gcloud dns policies create POLICY_NAME \
  --networks=VPC_NETWORK \
  --enable-inbound-forwarding

# List policies
gcloud dns policies list

# Delete
gcloud dns policies delete POLICY_NAME
```

## DNSSEC

```bash
# Enable DNSSEC on a zone
gcloud dns managed-zones update ZONE_NAME --dnssec-state=on

# Get DS records (for registrar)
gcloud dns dns-keys list --zone=ZONE_NAME \
  --filter="type=keySigning" \
  --format="value(ds_record())"

# Disable DNSSEC
gcloud dns managed-zones update ZONE_NAME --dnssec-state=off
```

## Troubleshooting

- **DNS not resolving** — check NS records at your registrar point to Cloud DNS name servers; use `dig` or `nslookup` to verify
- **"Zone not found"** — verify zone name (not domain name); zone names use hyphens, not dots
- **Record names must end with a dot** — e.g., `www.example.com.` (trailing dot)
- **Propagation delay** — DNS changes can take minutes to propagate; check TTL values
- **Transaction errors** — if a transaction fails, abort and start a new one; or use direct record management
- **Private zone not resolving** — ensure VPC is listed in the zone's network list
