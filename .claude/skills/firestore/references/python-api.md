# Firestore Python API Reference

## Table of Contents
- [Installation](#installation)
- [Client Initialization](#client-initialization)
- [Class Hierarchy](#class-hierarchy)
- [CRUD Operations](#crud-operations)
- [Field Transforms](#field-transforms)
- [Querying](#querying)
- [Pagination](#pagination)
- [Aggregation Queries](#aggregation-queries)
- [Collection Group Queries](#collection-group-queries)
- [Transactions](#transactions)
- [Batch Writes](#batch-writes)
- [Subcollections](#subcollections)
- [Real-Time Listeners](#real-time-listeners)
- [DocumentSnapshot](#documentsnapshot)
- [Imports Reference](#imports-reference)

## Installation

```bash
pip install google-cloud-firestore
```

Requires Python 3.7+. Uses gRPC transport (REST fallback available).

## Client Initialization

### google-cloud-firestore (Direct)

```python
from google.cloud import firestore

# Sync
db = firestore.Client(project="my-project")

# Async
db = firestore.AsyncClient(project="my-project")
```

Parameters: `project` (auto-detected if omitted), `credentials` (ADC if omitted), `database` (defaults to `"(default)"`), `client_options`.

### firebase-admin (Wrapper)

```python
import firebase_admin
from firebase_admin import credentials, firestore, firestore_async

app = firebase_admin.initialize_app()       # ADC
# or: firebase_admin.initialize_app(credentials.Certificate('sa.json'))

db = firestore.client()         # sync
db = firestore_async.client()   # async

# Cleanup async sessions
firebase_admin.delete_app(app)
```

Both expose identical Firestore APIs. Use `firebase-admin` when needing other Firebase services; use `google-cloud-firestore` directly for lighter dependencies.

### Regional Endpoint

```python
from google.api_core.client_options import ClientOptions
opts = ClientOptions(api_endpoint="nam5-firestore.googleapis.com")
db = firestore.Client(client_options=opts)
```

### Emulator

Set `FIRESTORE_EMULATOR_HOST=localhost:8080` — the client auto-detects it.

### Client Lifecycle

- **Singleton recommended**: create one client, reuse across requests.
- **Thread-safe** (sync). **Single event loop** (async) — create once per loop.
- gRPC channel cleaned up on garbage collection.

## Class Hierarchy

| Sync | Async | Purpose |
|------|-------|---------|
| `Client` | `AsyncClient` | Entry point |
| `CollectionReference` | `AsyncCollectionReference` | Collection ref |
| `DocumentReference` | `AsyncDocumentReference` | Document ref |
| `Query` | `AsyncQuery` | Query builder |
| `CollectionGroup` | `AsyncCollectionGroup` | Cross-collection query |
| `WriteBatch` | `AsyncWriteBatch` | Atomic batch writes |
| `Transaction` | `AsyncTransaction` | Read-write transaction |
| `AggregationQuery` | `AsyncAggregationQuery` | count/sum/avg |
| `DocumentSnapshot` | `DocumentSnapshot` | Immutable doc data (shared) |

## CRUD Operations

### Create / Set

```python
# set() — create or overwrite
doc_ref = db.collection("users").document("alice")
await doc_ref.set({"name": "Alice", "age": 30})

# set() with merge — only overwrite specified fields
await doc_ref.set({"age": 31}, merge=True)

# add() — auto-generate ID, returns (update_time, doc_ref)
update_time, ref = await db.collection("users").add({"name": "Bob"})

# create() — fails with Conflict if exists
await db.collection("users").document("carol").create({"name": "Carol"})
```

### Read

```python
# Single document
doc = await doc_ref.get()
if doc.exists:
    data = doc.to_dict()
    name = doc.get("name")

# All documents in collection (streaming — memory efficient)
async for doc in db.collection("users").stream():
    print(f"{doc.id} => {doc.to_dict()}")

# Async list comprehension
docs = [doc async for doc in db.collection("users").stream()]

# Batch get (multiple refs)
refs = [db.collection("users").document(uid) for uid in ["alice", "bob"]]
async for doc in db.get_all(refs):
    print(doc.to_dict())
```

### Update

```python
# Update specific fields (document must exist — raises NotFound otherwise)
await doc_ref.update({"age": 31})

# Nested field update with dot notation
await doc_ref.update({"address.city": "London"})
```

### Delete

```python
# Single document
await doc_ref.delete()

# Recursive delete (document + all subcollections)
count = await db.recursive_delete(db.collection("users").document("alice"))
```

Sync equivalents are identical without `await`.

## Field Transforms

Sentinel values for atomic server-side operations:

```python
from google.cloud import firestore

# Server timestamp
await doc_ref.update({"updated_at": firestore.SERVER_TIMESTAMP})

# Atomic increment/decrement
await doc_ref.update({"views": firestore.Increment(1)})
await doc_ref.update({"stock": firestore.Increment(-1)})

# Array add (only if not present)
await doc_ref.update({"tags": firestore.ArrayUnion(["python"])})

# Array remove (all instances)
await doc_ref.update({"tags": firestore.ArrayRemove(["deprecated"])})

# Delete field entirely
await doc_ref.update({"old_field": firestore.DELETE_FIELD})
```

## Querying

### Filter Operators

```python
from google.cloud.firestore_v1.base_query import FieldFilter, And, Or

# Operators: ==, !=, <, <=, >, >=, in, not-in, array_contains, array_contains_any
query = db.collection("cities").where(filter=FieldFilter("population", ">", 1_000_000))

# in (up to 30 values across all in/array_contains_any)
query = db.collection("cities").where(filter=FieldFilter("country", "in", ["US", "JP"]))

# array_contains
query = db.collection("cities").where(filter=FieldFilter("tags", "array_contains", "capital"))
```

### Composite Filters

```python
# OR
query = db.collection("cities").where(filter=Or([
    FieldFilter("capital", "==", True),
    FieldFilter("population", ">", 1_000_000),
]))

# AND (explicit)
query = db.collection("cities").where(filter=And([
    FieldFilter("state", ">=", "CA"),
    FieldFilter("state", "<=", "IN"),
]))

# Nested: OR of ANDs
query = db.collection("users").where(filter=Or([
    And([FieldFilter("role", "==", "admin"), FieldFilter("active", "==", True)]),
    And([FieldFilter("role", "==", "superadmin")]),
]))
```

### Chaining (implicit AND)

```python
query = (
    db.collection("cities")
    .where(filter=FieldFilter("state", "==", "CA"))
    .where(filter=FieldFilter("population", ">", 1_000_000))
)
```

### Ordering, Limiting, Projecting

```python
query = db.collection("cities").order_by("name")
query = db.collection("cities").order_by("name", direction=firestore.Query.DESCENDING)
query = db.collection("cities").order_by("name").limit(10)
query = db.collection("cities").order_by("name").limit_to_last(5).get()  # returns list
query = db.collection("cities").select(["name", "population"])  # field projection
```

### Executing Queries

```python
# get() — loads all into memory
results = await query.get()  # list[DocumentSnapshot]

# stream() — generator, memory-efficient
async for doc in query.stream():
    print(doc.to_dict())
```

## Pagination

Use cursor-based pagination. **Never use `offset()`** — skipped documents are still billed as reads.

```python
cities = db.collection("cities").order_by("population").limit(25)

# First page
docs = [d async for d in cities.stream()]
last = docs[-1]

# Next page — pass DocumentSnapshot directly
next_page = (
    db.collection("cities")
    .order_by("population")
    .start_after(last)
    .limit(25)
)
```

| Method | Boundary |
|--------|----------|
| `start_at(doc_or_fields)` | Inclusive |
| `start_after(doc_or_fields)` | Exclusive |
| `end_at(doc_or_fields)` | Inclusive |
| `end_before(doc_or_fields)` | Exclusive |

Pass either a `DocumentSnapshot` or a dict of field values matching the `order_by` fields.

## Aggregation Queries

Server-side aggregations — only result transmitted, not documents.

```python
# Count
result = await db.collection("cities").count().get()

# Sum
result = await db.collection("cities").sum("population").get()

# Average
result = await db.collection("cities").avg("population").get()
```

Cost: 1 read per 1,000 index entries matched (vs 1 read per document if fetching all).

## Collection Group Queries

Query across all collections/subcollections with the same name:

```python
query = db.collection_group("landmarks").where(
    filter=FieldFilter("type", "==", "museum")
)
async for doc in query.stream():
    print(f"{doc.reference.path}: {doc.to_dict()}")
```

Requires a collection group index.

## Transactions

Atomic read-then-write operations. All reads must occur before writes.

### Async Transaction

```python
transaction = db.transaction()

@firestore.async_transactional
async def transfer_funds(transaction, from_ref, to_ref, amount):
    from_doc = await from_ref.get(transaction=transaction)
    to_doc = await to_ref.get(transaction=transaction)

    from_balance = from_doc.get("balance")
    to_balance = to_doc.get("balance")

    if from_balance < amount:
        raise ValueError("Insufficient funds")

    transaction.update(from_ref, {"balance": from_balance - amount})
    transaction.update(to_ref, {"balance": to_balance + amount})

await transfer_funds(transaction, from_ref, to_ref, 100.0)
```

### Sync Transaction

```python
transaction = db.transaction()

@firestore.transactional
def transfer_funds(transaction, from_ref, to_ref, amount):
    from_doc = from_ref.get(transaction=transaction)
    # ... same logic without await
    transaction.update(from_ref, {"balance": from_balance - amount})
    transaction.update(to_ref, {"balance": to_balance + amount})

transfer_funds(transaction, from_ref, to_ref, 100.0)
```

Configuration: `db.transaction(max_attempts=10, read_only=False)` — default 5 retries.

Transaction methods: `get()`, `get_all()`, `create()`, `set()`, `update()`, `delete()`.

Constraints:
- Max **500 writes** per transaction
- Reads before writes
- Decorated function's **first parameter** must be `transaction`
- May retry up to `max_attempts` on contention

## Batch Writes

Atomic multi-document writes without reads.

```python
batch = db.batch()

batch.set(db.collection("cities").document("NYC"), {"name": "New York"})
batch.update(db.collection("cities").document("SF"), {"population": 884_363})
batch.delete(db.collection("cities").document("DEN"))

await batch.commit()
```

Max **500 operations** per batch. Each operation billed individually.

## Subcollections

```python
# Reference a subcollection
subcol = db.collection("users").document("alice").collection("orders")
# or: db.collection("users/alice/orders")

# Nested document reference
doc = db.document("users", "alice", "orders", "order123")
# or: db.document("users/alice/orders/order123")

# List subcollections
async for col in db.collection("users").document("alice").collections():
    print(col.id)
```

## Real-Time Listeners

**Sync only** — `AsyncDocumentReference` does not support `on_snapshot`.

```python
def on_snapshot(doc_snapshot, changes, read_time):
    for doc in doc_snapshot:
        print(f"Update: {doc.id} => {doc.to_dict()}")

# Document listener
watch = doc_ref.on_snapshot(on_snapshot)

# Collection/query listener
watch = db.collection("cities").on_snapshot(on_snapshot)

# Unsubscribe
watch.unsubscribe()
```

## DocumentSnapshot

```python
doc = await doc_ref.get()

doc.exists        # bool
doc.id            # str — document ID
doc.reference     # DocumentReference
doc.to_dict()     # dict | None
doc.get("field")  # specific field (supports dot notation: "a.b.c")
doc.create_time   # Timestamp
doc.update_time   # Timestamp
doc.read_time     # Timestamp
```

## Imports Reference

```python
from google.cloud import firestore

# Query filters
from google.cloud.firestore_v1.base_query import FieldFilter, And, Or

# Sentinels (also on firestore module)
firestore.SERVER_TIMESTAMP
firestore.DELETE_FIELD
firestore.ArrayUnion(values)
firestore.ArrayRemove(values)
firestore.Increment(value)

# Decorators
firestore.transactional           # sync
firestore.async_transactional     # async
```

Full module paths (rarely needed):
```python
from google.cloud.firestore_v1.async_client import AsyncClient
from google.cloud.firestore_v1.async_collection import AsyncCollectionReference
from google.cloud.firestore_v1.async_document import AsyncDocumentReference
from google.cloud.firestore_v1.async_query import AsyncQuery, AsyncCollectionGroup
from google.cloud.firestore_v1.async_transaction import AsyncTransaction
from google.cloud.firestore_v1.async_batch import AsyncWriteBatch
```
