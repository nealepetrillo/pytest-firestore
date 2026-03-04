# gcloud emulators — Local Development Emulators Reference

The gcloud CLI provides local emulators for testing against GCP services without incurring costs or requiring network access. Available emulators: **Firestore**, **Pub/Sub**, **Bigtable**, **Datastore**, and **Spanner**.

## Contents
- [Installation](#installation)
- [Common Pattern: start → env-init → run app](#common-pattern-start--env-init--run-app)
- [Firestore Emulator](#firestore-emulator)
- [Pub/Sub Emulator](#pubsub-emulator)
- [Bigtable Emulator](#bigtable-emulator)
- [Datastore Emulator](#datastore-emulator)
- [Spanner Emulator](#spanner-emulator)
- [Docker-Based Emulators](#docker-based-emulators)
- [Environment Variable Summary](#environment-variable-summary)
- [Troubleshooting](#troubleshooting)

## Installation

Emulators are installed as separate SDK components:

```bash
gcloud components install cloud-firestore-emulator
gcloud components install pubsub-emulator
gcloud components install bigtable
gcloud components install cloud-datastore-emulator
# Spanner emulator requires Docker (x86_64 has native binary on Linux)
gcloud components install cloud-spanner-emulator
```

Install all at once:
```bash
gcloud components install cloud-firestore-emulator pubsub-emulator bigtable cloud-datastore-emulator
```

## Common Pattern: start → env-init → run app

Every emulator follows the same workflow:
1. **Start** the emulator (runs in foreground, use separate terminal or `&`)
2. **Export** the environment variable via `env-init` (tells client libraries to use emulator)
3. **Run** your application — client libraries detect the env var automatically

```bash
# Terminal 1: Start emulator
gcloud beta emulators EMULATOR start [--host-port=HOST:PORT]

# Terminal 2: Set env vars and run app
$(gcloud beta emulators EMULATOR env-init)
python my_app.py
```

## Firestore Emulator

### Start
```bash
gcloud beta emulators firestore start
gcloud beta emulators firestore start --host-port=localhost:8080
gcloud beta emulators firestore start --rules=firestore.rules  # Security rules file
```

Default port: `8080`

### Environment
```bash
$(gcloud beta emulators firestore env-init)
# Sets: FIRESTORE_EMULATOR_HOST=localhost:8080
```

### Python Client
```python
import os
os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:8080"

from google.cloud import firestore
# No credentials needed when emulator host is set
db = firestore.Client(project="test-project")
doc_ref = db.collection("users").document("test")
doc_ref.set({"name": "Test User", "age": 30})
```

### Key Notes
- Supports Firestore Native mode and Datastore mode (`--database-mode=datastore-mode`)
- Data is ephemeral — lost when emulator stops
- Security rules can be tested with `--rules` flag
- UI not included (unlike Firebase Emulator Suite)

## Pub/Sub Emulator

### Start
```bash
gcloud beta emulators pubsub start
gcloud beta emulators pubsub start --host-port=localhost:8085
gcloud beta emulators pubsub start --project=my-project
```

Default port: `8085`

### Environment
```bash
$(gcloud beta emulators pubsub env-init)
# Sets: PUBSUB_EMULATOR_HOST=localhost:8085
# Optionally: PUBSUB_PROJECT_ID=my-project
```

### Python Client
```python
import os
os.environ["PUBSUB_EMULATOR_HOST"] = "localhost:8085"

from google.cloud import pubsub_v1

publisher = pubsub_v1.PublisherClient()
topic_path = publisher.topic_path("test-project", "my-topic")
publisher.create_topic(request={"name": topic_path})

future = publisher.publish(topic_path, b"Hello, Pub/Sub emulator!")
print(f"Published: {future.result()}")

subscriber = pubsub_v1.SubscriberClient()
sub_path = subscriber.subscription_path("test-project", "my-sub")
subscriber.create_subscription(request={"name": sub_path, "topic": topic_path})
```

### Key Notes
- Topics and subscriptions must be created programmatically (no pre-seeding)
- Push subscriptions are NOT supported in the emulator
- Data is ephemeral
- `--log-http` flag useful for debugging message flow

## Bigtable Emulator

### Start
```bash
gcloud beta emulators bigtable start
gcloud beta emulators bigtable start --host-port=localhost:8086
```

Default port: `8086`

### Environment
```bash
$(gcloud beta emulators bigtable env-init)
# Sets: BIGTABLE_EMULATOR_HOST=localhost:8086
```

### Python Client
```python
import os
os.environ["BIGTABLE_EMULATOR_HOST"] = "localhost:8086"

from google.cloud import bigtable

client = bigtable.Client(project="test-project", admin=True)
instance = client.instance("test-instance")
# Create table
table = instance.table("my-table")
column_family_id = "cf1"
table.create(column_families={column_family_id: None})
```

### Key Notes
- In-memory only, all data lost on restart
- No authentication required
- Supports the full Bigtable Data and Admin APIs

## Datastore Emulator

### Start
```bash
gcloud beta emulators datastore start
gcloud beta emulators datastore start --host-port=localhost:8081
gcloud beta emulators datastore start --data-dir=./datastore-data  # Persist data
gcloud beta emulators datastore start --consistency=1.0            # Strong consistency
```

Default port: `8081`

### Environment
```bash
$(gcloud beta emulators datastore env-init)
# Sets: DATASTORE_EMULATOR_HOST=localhost:8081
# Also: DATASTORE_EMULATOR_HOST_PATH=localhost:8081/datastore
# Also: DATASTORE_HOST=http://localhost:8081
# Also: DATASTORE_PROJECT_ID=my-project
```

### Python Client
```python
import os
os.environ["DATASTORE_EMULATOR_HOST"] = "localhost:8081"

from google.cloud import datastore
client = datastore.Client(project="test-project")
key = client.key("Task", "sample_task")
entity = datastore.Entity(key=key)
entity.update({"description": "Test task", "done": False})
client.put(entity)
```

### Key Notes
- Supports `--data-dir` for persisting data across restarts
- `--consistency` flag controls eventual consistency simulation (0.0 to 1.0)
- Consider using Firestore in Datastore mode instead for new projects

## Spanner Emulator

### Start
```bash
gcloud beta emulators spanner start
gcloud beta emulators spanner start --host-port=localhost:9010
```

Default ports: gRPC on `9010`, REST on `9020`

### Environment
```bash
$(gcloud beta emulators spanner env-init)
# Sets: SPANNER_EMULATOR_HOST=localhost:9010
```

### Python Client
```python
import os
os.environ["SPANNER_EMULATOR_HOST"] = "localhost:9010"

from google.cloud import spanner

client = spanner.Client(project="test-project")
instance_config = "emulator-config"
instance = client.instance("test-instance",
    configuration_name=f"projects/test-project/instanceConfigs/{instance_config}")
instance.create()

database = instance.database("test-db", ddl_statements=[
    "CREATE TABLE Users (UserId INT64 NOT NULL, Name STRING(100)) PRIMARY KEY (UserId)"
])
database.create()
```

### Key Notes
- Requires Docker on non-Linux x86_64 platforms
- Uses `emulator-config` as the instance config name
- Supports most Spanner DDL and DML, but some features may differ from production
- No IAM or fine-grained access control in emulator

## Docker-Based Emulators

Google provides a Docker image with all emulators pre-installed:
```bash
docker pull gcr.io/google.com/cloudsdktool/google-cloud-cli:emulators

# Run specific emulator:
docker run -p 8085:8085 gcr.io/google.com/cloudsdktool/google-cloud-cli:emulators \
  gcloud beta emulators pubsub start --host-port=0.0.0.0:8085
```

## Environment Variable Summary

| Emulator | Env Variable | Default Port |
|----------|-------------|--------------|
| Firestore | `FIRESTORE_EMULATOR_HOST` | 8080 |
| Pub/Sub | `PUBSUB_EMULATOR_HOST` | 8085 |
| Bigtable | `BIGTABLE_EMULATOR_HOST` | 8086 |
| Datastore | `DATASTORE_EMULATOR_HOST` | 8081 |
| Spanner | `SPANNER_EMULATOR_HOST` | 9010 (gRPC) |

## Troubleshooting

- **App not using emulator**: Verify env var is set in the same shell session as your app. Use `echo $EMULATOR_HOST` to confirm.
- **Port conflicts**: Use `--host-port` to specify an alternate port.
- **"emulator not installed"**: Run `gcloud components install COMPONENT_NAME`.
- **Spanner on Mac/Windows**: Ensure Docker is running; the emulator runs as a container.
- **Resetting emulator data**: Simply restart the emulator (all data is in-memory except Datastore with `--data-dir`).
- **Connecting from Docker containers**: Use `host.docker.internal` instead of `localhost` for the emulator host, or use Docker networking.
