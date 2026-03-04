# Firestore Cost Management Reference

## Table of Contents
- [Pricing Model](#pricing-model)
- [Free Tier](#free-tier)
- [What Counts as Operations](#what-counts-as-operations)
- [Listener Costs](#listener-costs)
- [Aggregation Query Costs](#aggregation-query-costs)
- [Index Cost Impact](#index-cost-impact)
- [Batch and Transaction Costs](#batch-and-transaction-costs)
- [Cost Optimization Strategies](#cost-optimization-strategies)
- [Common Cost Pitfalls](#common-cost-pitfalls)
- [Cost at Scale](#cost-at-scale)

## Pricing Model

### Per-Operation (Standard Edition, single region)

| Operation | Cost |
|-----------|------|
| Document reads | $0.06 / 100K |
| Document writes | $0.18 / 100K |
| Document deletes | $0.02 / 100K |

### Storage
- **$0.18 / GiB / month** — includes document data, metadata, field names (schemaless overhead), and all index entries

### Network
- Ingress: free
- First 10 GiB/month egress: free
- Multi-region locations (nam5, eur3) cost 2-3x more for storage

### Committed Use Discounts
- 1-year: 20% off operations
- 3-year: 40% off operations

## Free Tier

Resets **daily** (not monthly):

| Resource | Daily Free |
|----------|-----------|
| Reads | 50,000 |
| Writes | 20,000 |
| Deletes | 20,000 |
| Storage | 1 GiB total |
| Egress | 10 GiB/month |

Applies to one database per project. On Blaze plan, free tier is a daily credit.

## What Counts as Operations

### Reads
- Query returning N docs = **N reads** (minimum 1, even if 0 results)
- `offset()` — skipped docs are **still billed as reads**
- Firebase Console data viewer — browsing counts as reads
- Import/export operations generate reads
- `get_all()` with N refs = N reads

### Writes
- Each `set()`, `update()`, `add()`, `create()` = **1 write**
- No-op writes (identical data) are **still billed**
- Each `delete()` = 1 delete
- Field transforms (serverTimestamp, increment, arrayUnion) each add operations within a write

## Listener Costs

- **Connection itself**: free
- **Initial snapshot**: charged for every document in initial result set (500 docs = 500 reads)
- **Ongoing updates**: 1 read per document added, modified, or removed from result set
- **Reconnection (offline persistence enabled)**: if disconnected >30 min, re-reads entire result set
- **Reconnection (no offline persistence)**: every reconnect re-reads entire result set

**Cost principle**: long-lived listeners paying incremental costs are cheaper than repeated `get()` calls.

## Aggregation Query Costs

- **1 read per 1,000 index entries** matched (minimum 1 read)
- `count()` on 1,500 docs = 2 reads
- `count()` on 100,000 docs = 100 reads (vs 100,000 if fetching all docs)

Always prefer aggregation queries over fetching-and-counting client-side.

## Index Cost Impact

- **Storage**: every index entry uses storage ($0.18/GiB/month)
- **Write amplification**: writes update ALL indexes referencing the document
- Unused composite indexes waste storage and slow writes
- **Exempt** fields from automatic indexing if never queried (large text, blobs, metadata)

## Batch and Transaction Costs

Batches and transactions do **NOT** save money — each operation billed individually.

- Batch with 5 writes = 5 billed writes
- Transaction reads are also billed
- **Failed transaction retries**: all reads/writes in the failed attempt are still billed

Benefits are atomicity and reduced network round-trips, not cost savings.

## Cost Optimization Strategies

### Query Design
1. **Never use `offset()`** — use cursor pagination (`start_after()`)
2. **Use `limit()`** — fetch only what you need
3. **Use `select()`** — field projection reduces bandwidth (still 1 read per doc)
4. **Use aggregation queries** — `count()`, `sum()`, `avg()` instead of fetching all docs

### Caching
5. **Application-level caching** — in-memory or Redis for frequently accessed, rarely changed data
6. **Enable offline persistence** in client SDKs to reduce redundant reads

### Data Model
7. **Keep documents small** — reduces storage and bandwidth costs
8. **Denormalize strategically** — store computed/aggregated values at write time to avoid expensive reads
9. **Use subcollections** instead of unbounded arrays

### Index Management
10. **Delete unused composite indexes**
11. **Add index exemptions** for unqueried fields (large text, blobs)
12. **Audit indexes regularly**

### Monitoring
13. **Set Google Cloud Budget Alerts** at 50%, 80%, 100%
14. **Use Firebase Usage dashboard** for real-time operation tracking
15. **Enable App Check** to prevent unauthorized access spiking bills

## Common Cost Pitfalls

| Pitfall | Impact | Fix |
|---------|--------|-----|
| `offset()` pagination | Skipped docs billed as reads | Use `start_after()` cursors |
| Listening to entire collections | Initial snapshot reads every doc | Scope with `where()` + `limit()` |
| Browsing Firebase Console on prod | Console loads = billed reads | Use emulator for dev |
| No-op writes | Still billed | Accept or check before writing |
| Reconnection without persistence | Re-reads entire result set | Enable offline persistence |
| Excessive composite indexes | Storage + write slowdown | Audit and remove unused |
| Fetching docs to count | N reads for N docs | Use `count()` aggregation |
| Transaction retries | Failed attempts still billed | Keep transactions small/fast |
| TTL deletions | Billed as delete operations | Budget for TTL delete costs |
| Import/export operations | Generate read/write charges | Schedule during off-peak |

## Cost at Scale

Approximate monthly operation costs (Standard edition, single region, excluding storage/egress):

| Scale | Reads/day | Writes/day | ~Monthly |
|-------|-----------|------------|----------|
| Free tier | 50K | 20K | $0 |
| Small app | 500K | 100K | ~$12 |
| Medium app | 5M | 1M | ~$120 |
| Large app | 50M | 10M | ~$1,200 |
