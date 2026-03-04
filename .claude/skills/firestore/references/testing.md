# Firestore Testing Reference

## Table of Contents
- [Emulator Setup](#emulator-setup)
- [Python Client with Emulator](#python-client-with-emulator)
- [pytest Integration](#pytest-integration)
- [Async Testing](#async-testing)
- [Data Seeding](#data-seeding)

## Emulator Setup

### Prerequisites
- Node.js 16.0+
- Java JDK 11+
- Firebase CLI 8.14.0+

### Installation and Running

```bash
npm install -g firebase-tools
firebase init firestore
firebase emulators:start --only firestore          # default port 8080
firebase emulators:start --only firestore --project=test-project
```

### Data Import/Export

```bash
firebase emulators:start --export-on-exit=./seed-data
firebase emulators:start --import=./seed-data
```

### Emulator UI
Available at `http://localhost:4000` — browse collections, view request logs.

## Python Client with Emulator

Set the environment variable before creating the client:

```python
import os
os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:8080"

from google.cloud import firestore
db = firestore.AsyncClient(project="test-project")
```

The client auto-detects `FIRESTORE_EMULATOR_HOST` and creates insecure channels.

## pytest Integration

### Fixture Pattern

```python
import os
import pytest
import pytest_asyncio
from google.cloud import firestore


@pytest.fixture(scope="session", autouse=True)
def firestore_emulator():
    """Ensure FIRESTORE_EMULATOR_HOST is set."""
    host = os.environ.get("FIRESTORE_EMULATOR_HOST", "localhost:8080")
    os.environ["FIRESTORE_EMULATOR_HOST"] = host
    yield host


@pytest_asyncio.fixture
async def db(firestore_emulator):
    """Provide a Firestore AsyncClient connected to emulator."""
    client = firestore.AsyncClient(project="test-project")
    yield client


@pytest_asyncio.fixture
async def clean_collection(db):
    """Factory fixture to create and clean up test collections."""
    collections = []

    def _make(name: str):
        ref = db.collection(name)
        collections.append(ref)
        return ref

    yield _make

    # Cleanup: delete all documents in created collections
    for col_ref in collections:
        async for doc in col_ref.stream():
            await doc.reference.delete()
```

### Test Example

```python
import pytest

@pytest.mark.asyncio
async def test_create_and_read_document(db, clean_collection):
    users = clean_collection("test_users")

    await users.document("alice").set({"name": "Alice", "age": 30})

    doc = await users.document("alice").get()
    assert doc.exists
    assert doc.to_dict() == {"name": "Alice", "age": 30}


@pytest.mark.asyncio
async def test_query(db, clean_collection):
    cities = clean_collection("test_cities")

    await cities.document("sf").set({"name": "SF", "pop": 884_363})
    await cities.document("la").set({"name": "LA", "pop": 3_979_576})
    await cities.document("ny").set({"name": "NY", "pop": 8_336_817})

    from google.cloud.firestore_v1.base_query import FieldFilter
    query = cities.where(filter=FieldFilter("pop", ">", 1_000_000))
    docs = [doc async for doc in query.stream()]

    assert len(docs) == 2
    names = {d.to_dict()["name"] for d in docs}
    assert names == {"LA", "NY"}


@pytest.mark.asyncio
async def test_transaction(db, clean_collection):
    accounts = clean_collection("test_accounts")

    await accounts.document("a").set({"balance": 100})
    await accounts.document("b").set({"balance": 50})

    transaction = db.transaction()

    @firestore.async_transactional
    async def transfer(transaction, from_ref, to_ref, amount):
        from_doc = await from_ref.get(transaction=transaction)
        to_doc = await to_ref.get(transaction=transaction)
        transaction.update(from_ref, {"balance": from_doc.get("balance") - amount})
        transaction.update(to_ref, {"balance": to_doc.get("balance") + amount})

    await transfer(
        transaction,
        accounts.document("a"),
        accounts.document("b"),
        30,
    )

    a = await accounts.document("a").get()
    b = await accounts.document("b").get()
    assert a.get("balance") == 70
    assert b.get("balance") == 80
```

## Async Testing

### pyproject.toml Configuration

```toml
[tool.pytest.ini_options]
asyncio_mode = "auto"  # or "strict" with explicit @pytest.mark.asyncio
```

### Sync Client Testing

Use `firestore.Client` instead of `AsyncClient` — no async fixtures needed:

```python
@pytest.fixture
def db(firestore_emulator):
    return firestore.Client(project="test-project")
```

## Data Seeding

### Fixture-Based Seeding

```python
@pytest_asyncio.fixture
async def seeded_db(db):
    """Seed database with test data."""
    batch = db.batch()
    cities = [
        ("sf", {"name": "San Francisco", "state": "CA", "pop": 884_363}),
        ("la", {"name": "Los Angeles", "state": "CA", "pop": 3_979_576}),
        ("ny", {"name": "New York", "state": "NY", "pop": 8_336_817}),
    ]
    for doc_id, data in cities:
        batch.set(db.collection("cities").document(doc_id), data)
    await batch.commit()
    yield db
    # Cleanup
    for doc_id, _ in cities:
        await db.collection("cities").document(doc_id).delete()
```

### Emulator Reset

For full reset between test runs, restart the emulator or use the REST API:

```python
import httpx

async def clear_emulator(project: str = "test-project"):
    """Clear all data in the Firestore emulator."""
    host = os.environ.get("FIRESTORE_EMULATOR_HOST", "localhost:8080")
    url = f"http://{host}/emulator/v1/projects/{project}/databases/(default)/documents"
    async with httpx.AsyncClient() as client:
        await client.delete(url)
```
