# pytest-playwright & pytest-playwright-asyncio

## Installation
```bash
pip install pytest-playwright
playwright install              # install browser binaries

# For async:
pip install pytest-playwright-asyncio
```

## Fixtures

### Session-scoped (shared)
| Fixture | Description |
|---------|-------------|
| `playwright` | Playwright API instance |
| `browser_type` | BrowserType (chromium/firefox/webkit) |
| `browser` | Launched Browser instance |
| `browser_name` | Browser name string |
| `browser_channel` | Channel string |
| `is_chromium`, `is_firefox`, `is_webkit` | Boolean type checks |

### Function-scoped (per test)
| Fixture | Description |
|---------|-------------|
| `page` | Fresh Page (isolated context) |
| `context` | Fresh BrowserContext |
| `new_context` | Factory for additional contexts (multi-user testing) |

## CLI Options

```bash
pytest --headed                     # visible browser
pytest --browser chromium           # specific browser (repeatable)
pytest --browser firefox --browser webkit  # multiple browsers
pytest --browser-channel chrome     # use installed Chrome
pytest --slowmo 500                 # slow down by ms
pytest --device "iPhone 13"         # device emulation
pytest --output test-results        # artifact directory

# Artifacts
pytest --tracing on                 # on / off / retain-on-failure
pytest --video on                   # on / off / retain-on-failure
pytest --screenshot on              # on / off / only-on-failure
pytest --full-page-screenshot       # full page on failure
```

## Configuration

### Base URL
```ini
# pyproject.toml
[tool.pytest.ini_options]
base_url = "http://localhost:8080"
```
```python
def test_home(page):
    page.goto("/")  # resolves to http://localhost:8080/
```
Or CLI: `pytest --base-url http://localhost:8080`

### Custom Browser Context
```python
@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "ignore_https_errors": True,
        "viewport": {"width": 1920, "height": 1080},
        "locale": "en-US",
    }
```

### Per-Test Context
```python
@pytest.mark.browser_context_args(timezone_id="Europe/Berlin", locale="de-DE")
def test_german_locale(page):
    ...
```

### Device Emulation
```python
@pytest.fixture(scope="session")
def browser_context_args(browser_context_args, playwright):
    iphone = playwright.devices["iPhone 13"]
    return {**browser_context_args, **iphone}
```

### Authenticated State
```python
@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {**browser_context_args, "storage_state": "auth_state.json"}
```

### Remote Browsers
```python
@pytest.fixture(scope="session")
def connect_options():
    return {"ws_endpoint": "ws://remote-browser:3000"}
```

### Custom Launch Args
```python
@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    return {**browser_type_launch_args, "args": ["--disable-gpu"]}
```

## Markers

```python
@pytest.mark.skip_browser("firefox")
def test_chromium_only(page): ...

@pytest.mark.only_browser("chromium")
def test_chromium_specific(page): ...
```

## Multi-User Testing
```python
def test_chat(page, new_context):
    # User 1
    page.goto("/chat")

    # User 2
    context2 = new_context()
    page2 = context2.new_page()
    page2.goto("/chat")
```

## Parallel Execution
```bash
pip install pytest-xdist
pytest --numprocesses auto          # or -n auto
```

## Async Version

Requires `pytest-asyncio>=0.26.0`. Note: pytest-asyncio 1.0+ removed the `event_loop` fixture; use `loop_scope` parameter instead.

```ini
# pyproject.toml
[tool.pytest.ini_options]
asyncio_default_test_loop_scope = "session"
```

```python
import pytest

@pytest.mark.asyncio(loop_scope="session")
async def test_home(page):
    await page.goto("https://example.com")
    title = await page.title()
    assert title == "Example Domain"
```

All Playwright interactions must be `await`-ed in async mode.

## Common Patterns

### Screenshot on failure (automatic)
```bash
pytest --screenshot only-on-failure --output test-results
```

### Trace recording for debugging
```bash
pytest --tracing retain-on-failure
# View: playwright show-trace test-results/trace.zip
```

### Network interception
```python
def test_mock_api(page):
    page.route("**/api/data", lambda route: route.fulfill(
        status=200, json={"key": "mocked"}
    ))
    page.goto("/dashboard")
```
