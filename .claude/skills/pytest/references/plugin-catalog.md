# Pytest Plugin Catalog

The official pytest plugin list contains **1,745+ plugins**. Below are plugins organized by common use cases. For the full list see https://docs.pytest.org/en/stable/reference/plugin_list.html

## Coverage & Profiling
- **pytest-cov** -- Coverage measurement (most popular)
- **pytest-benchmark** -- Benchmark code with calibration
- **pytest-codspeed** -- CodSpeed benchmarks
- **pytest-durations** -- Report execution time
- **pytest-austin** -- Austin profiler integration
- **pytest-codecarbon** -- Measure carbon emissions

## Parallel & Distribution
- **pytest-xdist** -- Distributed/parallel testing across CPUs/machines
- **pytest-asyncio-concurrent** -- Concurrent async tests
- **pytest-parallel** -- Parallel test execution
- **pytest-circleci-parallelized** -- CircleCI worker distribution

## Async
- **pytest-asyncio** -- asyncio support
- **pytest-aio** -- Async testing
- **pytest-trio** -- Trio support
- **pytest-twisted** -- Twisted support
- **pytest-anyio** -- AnyIO support (built into anyio)
- **pytest-curio** -- Curio support
- **pytest-eventlet** -- Eventlet support

## Mocking & Patching
- **pytest-mock** -- unittest.mock wrapper (mocker fixture)
- **pytest-automock** -- Record/replay mocking
- **pytest-stub** -- Lightweight stubbing
- **pytest-httpserver** -- Mock HTTP server
- **pytest-responses** -- Mock requests library
- **pytest-aioresponses** -- Mock aiohttp
- **pytest-recording** -- VCR.py integration (HTTP recording)
- **pytest-vcr** -- VCR cassette recording

## Web & Browser Testing
- **pytest-playwright** -- Playwright browser automation (sync)
- **pytest-playwright-asyncio** -- Playwright (async)
- **pytest-selenium** -- Selenium WebDriver
- **pytest-base-url** -- Base URL fixture
- **pytest-axe** -- Accessibility testing with axe-core
- **pytest-flask** -- Flask application testing
- **pytest-django** -- Django integration
- **pytest-fastapi** -- FastAPI testing
- **pytest-aiohttp** -- aiohttp testing

## Database
- **pytest-postgresql** -- PostgreSQL fixtures/factories
- **pytest-mysql** -- MySQL fixtures
- **pytest-mongo** -- MongoDB fixtures
- **pytest-redis** -- Redis fixtures
- **pytest-dynamodb** -- DynamoDB fixtures
- **pytest-elasticsearch** -- Elasticsearch fixtures
- **pytest-databases** -- Reusable database fixtures
- **pytest-bigquery-mock** -- BigQuery mocking
- **pytest-alembic** -- Verify alembic migrations

## Docker & Containers
- **pytest-docker** -- Docker/Docker Compose fixtures
- **pytest-docker-compose** -- Manage containers
- **pytest-docker-tools** -- Docker integration tests
- **pytest-container** -- Container-based fixtures
- **pytest-testcontainers** -- Testcontainers integration

## BDD
- **pytest-bdd** -- BDD for pytest
- **pytest-bdd-ng** -- Next-generation BDD
- **pytest-eucalyptus** -- BDD plugin

## Reporting
- **pytest-html** -- HTML reports
- **pytest-json-report** -- JSON reports
- **pytest-csv** -- CSV output
- **pytest-allure-adaptor** -- Allure reports
- **pytest-emoji** -- Emoji test output
- **pytest-clarity** -- Colorful diff output
- **pytest-sugar** -- Better terminal output

## Test Organization
- **pytest-dependency** -- Manage test dependencies
- **pytest-ordering** -- Test execution order
- **pytest-randomly** -- Random test order (exposes state deps)
- **pytest-cases** -- Separate test code from test cases
- **pytest-lazy-fixture** -- Use fixtures in parametrize
- **pytest-factoryboy** -- Factory Boy integration
- **pytest-faker** -- Faker integration

## Retry & Flaky Tests
- **pytest-rerunfailures** -- Rerun failed tests
- **pytest-flakefinder** -- Find flaky tests
- **pytest-retry** -- Retry failed tests
- **pytest-repeat** -- Repeat tests

## Environment & Config
- **pytest-env** -- Set environment variables
- **pytest-dotenv** -- Load .env files
- **pytest-envvars** -- Validate env var usage
- **pytest-venv** -- Virtual environment fixtures
- **pytest-freezegun** -- Time freezing
- **pytest-freezer** -- Freeze time

## File & Data
- **pytest-datadir** -- Test data directories
- **pytest-datafiles** -- tmp_path with predefined files
- **pytest-tmp-files** -- Declarative temp file trees
- **pytest-regressions** -- Regression testing
- **pytest-snapshot** -- Snapshot testing

## Linting & Style
- **pytest-flake8** -- Flake8 checking
- **pytest-black** -- Black formatting
- **pytest-mypy** -- Mypy type checking
- **pytest-pylint** -- Pylint integration

## CI/CD Integration
- **pytest-github-actions-annotate-failures** -- GitHub Actions annotations
- **pytest-azurepipelines** -- Azure Pipelines format
- **pytest-buildkite** -- Buildkite integration
- **pytest-custom-exit-code** -- Custom exit codes

## Process & System
- **pytest-bg-process** -- Background process management
- **pytest-timeout** -- Test timeouts
- **pytest-console-scripts** -- Test console scripts
- **pytest-subprocess** -- Mock subprocess calls
- **pytest-blockage** -- Disable network requests

## Debugging
- **pytest-pudb** -- PuDB debugger
- **pytest-pdb** -- PDB integration
- **pytest-faulthandler** -- Fault handler (built-in now)
- **pytest-bisect-tests** -- Find state-leaking tests

## Typing
- **pytest-mypy-plugins** -- Test mypy plugins
- **pytest-beartype** -- Beartype checking
