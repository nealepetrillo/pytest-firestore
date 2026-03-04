# Firestore Data Model, Types, Indexes, and Limits

## Table of Contents
- [Data Model](#data-model)
- [Data Types](#data-types)
- [Indexes](#indexes)
- [Query Capabilities and Limitations](#query-capabilities-and-limitations)
- [Security Rules](#security-rules)
- [TTL Policies](#ttl-policies)
- [Limits](#limits)
- [Data Modeling Patterns](#data-modeling-patterns)

## Data Model

**Documents**: fundamental unit of storage. Key-value fields mapping to values. Identified by unique ID within parent collection. Max 1 MiB.

**Collections**: containers holding documents only. Created implicitly when a document is written.

**Subcollections**: collections nested within a document. Path alternates: `collection/document/subcollection/document`. Up to 100 levels deep.

**Document references**: a data type storing a pointer to another document (enables relationships without denormalization).

Key rules:
- Paths always alternate collection/document
- Deleting a document does **NOT** delete its subcollections
- A document can exist with no fields (as subcollection container)

### Maps vs Subcollections
- **Maps** (nested objects): small, bounded, co-accessed data always read together
- **Subcollections**: large, unbounded, independently queryable data

## Data Types

| Type | Python Type | Notes |
|------|-------------|-------|
| `null` | `None` | Sorted first |
| `boolean` | `bool` | false < true |
| `integer` | `int` | 64-bit signed |
| `double` | `float` | 64-bit IEEE 754 |
| `timestamp` | `datetime.datetime` | Microsecond precision |
| `string` | `str` | UTF-8, max ~1 MiB |
| `bytes` | `bytes` | Max ~1 MiB |
| `reference` | `DocumentReference` | Path to another document |
| `geoPoint` | `GeoPoint` | Lat/long |
| `array` | `list` | Ordered, mixed types, no nested arrays |
| `map` | `dict` | String keys, any value type |

Firestore is schemaless — documents in the same collection can have different fields/types. Field names stored per-document (storage overhead).

## Indexes

### Automatic (Single-Field)
- Created for every field in every document automatically
- Non-array/map fields: ascending + descending indexes
- Array fields: `array-contains` index
- Powers basic equality and range queries on single fields

### Composite (Manual)
- Required for multi-field filter/sort queries
- Must be explicitly created (console, CLI, or Admin SDK)
- Firestore error messages include a link to create the missing index
- Max **200** composite indexes per database

### Exempt Fields
- Override automatic indexing for specific fields
- Use for: large text, blobs, high-write-rate fields, never-queried fields
- Reduces storage costs and write latency

### Index Merging
Firestore can combine multiple single-field indexes for some compound queries without requiring a composite index.

## Query Capabilities and Limitations

### Supported Operators
`==`, `!=`, `<`, `<=`, `>`, `>=`, `in`, `not-in`, `array_contains`, `array_contains_any`, `AND`, `OR`

### Key Limitations
- `in` / `array_contains_any`: combined max **30 disjunctions**
- `not-in`: max **10 values**
- Cannot combine `not-in` and `!=`
- Range/inequality filters: up to **10 fields** per query
- `array_contains`: at most **one** per disjunction group
- OR queries: max **30 disjunctions** (DNF)
- No native JOINs — denormalize or use multiple queries
- No full-text search — use external service (Algolia, Typesense, Elasticsearch)
- Security rules are NOT filters — query must match rule constraints or entire query is rejected

### Collection Group Queries
- `collection_group("name")` queries all collections with that name across the database
- Requires collection group index

## Security Rules

```
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
  }
}
```

Key variables: `request.auth`, `request.resource.data` (incoming), `resource.data` (existing), `request.time`.

Operations: `read` = `get` + `list`; `write` = `create` + `update` + `delete`.

Rules are NOT filters — queries must provably satisfy rules or they fail entirely.

## TTL Policies

- Designate a `Timestamp` field as TTL expiration field at collection group level
- Documents deleted when current time exceeds timestamp
- Deletion is **not instantaneous** — typically within 24 hours
- Expired documents **still appear in queries** until actually deleted
- TTL deletes are **billed** as delete operations
- Does NOT delete subcollections

## Limits

| Limit | Value |
|-------|-------|
| Max document size | 1 MiB |
| Max fields per document | 20,000 (including nested) |
| Max subcollection depth | 100 levels |
| Max field path depth | 20 segments |
| Max field name size | 1,500 bytes |
| Max writes per transaction/batch | 500 |
| Sustained write rate per document | 1/second (soft) |
| Max composite indexes | 200 |
| Max single-field exemptions | 200 |
| Max `in`/`array_contains_any` values | 30 |
| Max `not-in` values | 10 |
| Max inequality filter fields | 10 |
| Max OR disjunctions | 30 (DNF) |
| Transaction retries (default) | 5 |
| Max document path length | 6,144 chars |

The 1 write/sec/document limit is soft — brief bursts tolerated, sustained writes cause contention.

## Data Modeling Patterns

### Denormalization
Store computed/aggregated values at write time to avoid expensive reads:
```python
# Instead of counting orders with a query each time:
await user_ref.update({"order_count": firestore.Increment(1)})
```

### Document Fan-Out
Write summary data to multiple locations during writes:
```python
batch = db.batch()
batch.set(order_ref, order_data)
batch.update(user_ref, {"last_order": order_data["id"], "total_spent": firestore.Increment(order_data["total"])})
await batch.commit()
```

### Distributed Counters
For high-write-rate counters, shard across multiple documents:
```python
import random
shard_id = random.randint(0, NUM_SHARDS - 1)
shard_ref = doc_ref.collection("shards").document(str(shard_id))
await shard_ref.update({"count": firestore.Increment(1)})

# Read: sum all shards
total = 0
async for shard in doc_ref.collection("shards").stream():
    total += shard.to_dict().get("count", 0)
```

### Bucketing for Time-Series
Aggregate events into time-bucketed documents to reduce document count:
```python
bucket_id = timestamp.strftime("%Y-%m-%d-%H")
bucket_ref = db.collection("metrics").document(bucket_id)
await bucket_ref.set({
    "count": firestore.Increment(1),
    "total": firestore.Increment(value),
}, merge=True)
```
