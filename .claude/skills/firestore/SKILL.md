---
name: firestore
description: >
  Google Cloud Firestore expertise for Python applications with sync and async (AsyncIO) APIs,
  cost-aware data modeling, and production patterns. Use when: (1) Writing Python code that
  reads/writes data to Firestore, (2) Designing Firestore data models or schemas,
  (3) Building async Python services with Firestore using AsyncClient, (4) Writing queries,
  transactions, batch writes, or aggregations, (5) Optimizing Firestore costs (reads, writes,
  indexes), (6) Setting up Firestore testing with the emulator, (7) Any task involving
  google-cloud-firestore or firebase-admin Python packages.
---

# Firestore

Python-focused expertise for Google Cloud Firestore — covering the `google-cloud-firestore`
package, AsyncIO patterns, query design, cost management, and testing.

## Quick Start

### AsyncClient (preferred for async apps)

```python
from google.cloud import firestore

db = firestore.AsyncClient(project="my-project")

# Create
await db.collection("users").document("alice").set({"name": "Alice", "age": 30})

# Read
doc = await db.collection("users").document("alice").get()
data = doc.to_dict()  # {"name": "Alice", "age": 30}

# Query
from google.cloud.firestore_v1.base_query import FieldFilter
async for doc in db.collection("users").where(filter=FieldFilter("age", ">=", 18)).stream():
    print(doc.id, doc.to_dict())

# Update atomically
await db.collection("users").document("alice").update({"age": firestore.Increment(1)})
```

### Sync Client

```python
db = firestore.Client(project="my-project")
doc = db.collection("users").document("alice").get()
for doc in db.collection("users").stream():
    print(doc.id, doc.to_dict())
```

Create one client instance and reuse it (singleton pattern). The sync client is thread-safe.
The async client should live within a single event loop.

## Key Patterns

### Transactions (read-then-write atomicity)

```python
transaction = db.transaction()

@firestore.async_transactional
async def transfer(transaction, from_ref, to_ref, amount):
    from_snap = await from_ref.get(transaction=transaction)
    to_snap = await to_ref.get(transaction=transaction)
    transaction.update(from_ref, {"balance": from_snap.get("balance") - amount})
    transaction.update(to_ref, {"balance": to_snap.get("balance") + amount})

await transfer(transaction, from_ref, to_ref, 100)
```

All reads before writes. Max 500 writes. Default 5 retries on contention.

### Batch Writes (atomic multi-doc writes, no reads)

```python
batch = db.batch()
batch.set(ref1, data1)
batch.update(ref2, {"field": "value"})
batch.delete(ref3)
await batch.commit()  # max 500 operations
```

### Field Transforms

```python
firestore.SERVER_TIMESTAMP   # server-generated timestamp
firestore.Increment(1)       # atomic increment/decrement
firestore.ArrayUnion(["x"])  # add to array if not present
firestore.ArrayRemove(["x"]) # remove from array
firestore.DELETE_FIELD        # remove field entirely
```

### Pagination (always use cursors, never offset)

```python
query = db.collection("items").order_by("created").limit(25)
docs = [d async for d in query.stream()]
# Next page:
next_q = db.collection("items").order_by("created").start_after(docs[-1]).limit(25)
```

`offset()` bills for skipped documents — always use `start_after()`/`start_at()` instead.

### Aggregations

```python
count = await db.collection("users").count().get()         # 1 read per 1K docs
total = await db.collection("orders").sum("amount").get()
avg   = await db.collection("orders").avg("amount").get()
```

Far cheaper than fetching all documents to compute client-side.

## Cost Awareness

Every Firestore operation has a direct cost. Key principles:

- **Reads**: $0.06/100K. A query returning N docs = N reads (minimum 1).
- **Writes**: $0.18/100K. No-op writes still billed. Batches/transactions don't reduce cost.
- **`offset()` is a cost trap** — skipped docs still billed as reads. Use cursor pagination.
- **Aggregation queries** cost ~1 read per 1K docs vs 1 read per doc if fetching all.
- **Index exemptions** — exempt large/unqueried fields to reduce storage and write costs.
- **Console browsing** on production databases generates billed reads.

For detailed pricing tables and optimization strategies, see [references/cost-management.md](references/cost-management.md).

## Reference Files

- **[references/python-api.md](references/python-api.md)** — Complete Python API reference: client init, CRUD, queries, filters (FieldFilter/And/Or), pagination, aggregations, transactions, batch writes, subcollections, real-time listeners, DocumentSnapshot, imports
- **[references/cost-management.md](references/cost-management.md)** — Pricing model, free tier, what counts as operations, listener costs, index cost impact, optimization strategies, common pitfalls, cost-at-scale estimates
- **[references/data-model.md](references/data-model.md)** — Documents/collections/subcollections, supported data types, indexes (auto/composite/exempt), query capabilities and limits, security rules, TTL policies, platform limits, data modeling patterns (denormalization, distributed counters, bucketing)
- **[references/testing.md](references/testing.md)** — Firestore emulator setup, Python client with emulator, pytest fixtures for async testing, data seeding, emulator reset
