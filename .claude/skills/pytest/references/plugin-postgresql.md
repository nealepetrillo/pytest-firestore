# pytest-postgresql

Requires: Python>=3.9, psycopg>=3.0 (default) or psycopg2 (optional extra)

Supports PostgreSQL 12, 13, 14, 15, 16.

## Installation
```bash
pip install pytest-postgresql
# Default driver (psycopg v3):
pip install psycopg
# Alternative driver:
pip install pytest-postgresql[psycopg2]
```

## Quick Start
```python
def test_query(postgresql):
    with postgresql.cursor() as cur:
        cur.execute("CREATE TABLE t (id serial PRIMARY KEY, name text)")
        postgresql.commit()
        cur.execute("INSERT INTO t (name) VALUES ('Alice')")
        postgresql.commit()
        cur.execute("SELECT * FROM t")
        assert cur.fetchone()[1] == "Alice"
```

## Fixtures

| Fixture | Scope | Driver | Description |
|---------|-------|--------|-------------|
| `postgresql` | function | psycopg (v3) | Connected `psycopg.Connection` to fresh test DB |
| `postgresql_psycopg2` | function | psycopg2 | Connected `psycopg2` connection to fresh test DB |
| `postgresql_proc` | session | N/A | Starts/stops PostgreSQL server process |
| `postgresql_noproc` | session | N/A | Connects to existing PostgreSQL (Docker/CI) |

Each test gets a **clean database** (dropped/recreated between tests).

## Factory Functions

```python
from pytest_postgresql import factories

# Custom process fixture
pg_proc = factories.postgresql_proc(
    port=None,              # random port
    user="testuser",
    unixsocketdir="/var/run",
)

# psycopg (v3) client fixture from process
pg = factories.postgresql("pg_proc", dbname="mydb")

# psycopg2 client fixture from process
pg2 = factories.postgresql_psycopg2("pg_proc", dbname="mydb")

# No-process (existing server)
pg_noproc = factories.postgresql_noproc(
    host="postgres-service", port=5432, user="ci", password="secret"
)
pg_ext = factories.postgresql("pg_noproc")
```

## Factory Parameters

### `factories.postgresql_proc`

| Parameter | Description | Default |
|-----------|-------------|---------|
| `executable` | Path to `pg_ctl` | auto-detected |
| `host` | Hostname to listen on | `127.0.0.1` |
| `port` | Port (None = random free port) | `None` |
| `user` | PostgreSQL user | `postgres` |
| `password` | Password | `None` |
| `dbname` | Default database name | `tests` |
| `options` | PostgreSQL server options | `""` |
| `startparams` | Params passed to `pg_ctl start` | `""` |
| `unixsocketdir` | Unix socket directory | `$TMPDIR` |
| `logs_prefix` | Log file name prefix | `""` |
| `postgres_options` | Options passed to postgres process | `""` |
| `load` | SQL files / callables for template DB | `None` |

### `factories.postgresql` / `factories.postgresql_psycopg2`

| Parameter | Description | Default |
|-----------|-------------|---------|
| `process_fixture_name` | Name of process fixture | `"postgresql_proc"` |
| `dbname` | Database name | process fixture's dbname |
| `load` | SQL files / callables to load | `None` |
| `isolation_level` | Transaction isolation level | driver default |

### `factories.postgresql_noproc`

| Parameter | Description | Default |
|-----------|-------------|---------|
| `host` | Hostname | `localhost` |
| `port` | Port | `5432` |
| `user` | PostgreSQL user | `postgres` |
| `password` | Password | `None` |
| `dbname` | Database name | `tests` |
| `options` | Connection options | `""` |

## Pre-populating Databases

The `load` parameter accepts SQL files, dotted import paths, or callables:
```python
def load_schema(connection):
    cur = connection.cursor()
    cur.execute("CREATE TABLE t (id serial PRIMARY KEY, name text)")
    connection.commit()
    cur.close()

pg_proc = factories.postgresql_proc(
    load=[
        "path/to/schema.sql",         # SQL file path
        load_schema,                   # callable (receives connection)
    ]
)
```

Template database is populated **once per session**, then cloned per test (fast).

## Configuration

Resolution order: factory args > CLI > pytest.ini

| CLI Flag | INI Option | Default |
|----------|------------|---------|
| `--postgresql-exec` | `postgresql_exec` | auto-detected |
| `--postgresql-host` | `postgresql_host` | 127.0.0.1 |
| `--postgresql-port` | `postgresql_port` | random |
| `--postgresql-user` | `postgresql_user` | postgres |
| `--postgresql-password` | `postgresql_password` | (empty) |
| `--postgresql-dbname` | `postgresql_dbname` | tests |
| `--postgresql-startparams` | `postgresql_startparams` | (empty) |
| `--postgresql-unixsocketdir` | `postgresql_unixsocketdir` | $TMPDIR |
| `--postgresql-options` | `postgresql_options` | (empty) |
| `--postgresql-logsprefix` | `postgresql_logsprefix` | (empty) |
| `--postgresql-postgres-options` | `postgresql_postgres_options` | (empty) |

## PostgreSQLExecutor Attributes

The process fixture returns an executor with:
- `.host`, `.port`, `.user`, `.password`, `.dbname`
- `.version` — PostgreSQL server version
- `.unixsocketdir`, `.executable`, `.logfile`, `.datadir`

## Docker Integration

```python
# conftest.py
pg_docker = factories.postgresql_noproc()
postgresql = factories.postgresql("pg_docker", dbname="test")
```
```bash
docker run --name pg -e POSTGRES_PASSWORD=secret -d postgres
pytest --postgresql-host=172.17.0.2 --postgresql-password=secret
```

## SQLAlchemy Integration

```python
@pytest.fixture
def db_session(postgresql):
    info = postgresql.info
    url = f"postgresql+psycopg://{info.user}:@{info.host}:{info.port}/{info.dbname}"
    engine = create_engine(url, poolclass=NullPool)
    Base.metadata.create_all(engine)
    Session = scoped_session(sessionmaker(bind=engine))
    yield Session()
    Session.close()
    Base.metadata.drop_all(engine)
```

## DatabaseJanitor (Advanced)

Manual database management outside fixtures:
```python
from pytest_postgresql.janitor import DatabaseJanitor

with DatabaseJanitor(
    user=pg_proc.user, host=pg_proc.host, port=pg_proc.port,
    dbname="custom_db", version=pg_proc.version, password="secret",
):
    with psycopg.connect(...) as conn:
        # use connection
        ...
```
