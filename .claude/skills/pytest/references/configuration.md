# Pytest Configuration Reference

## Table of Contents
- [Config File Types & Precedence](#config-file-types--precedence)
- [Root Directory Determination](#root-directory-determination)
- [INI Options](#ini-options)
- [CLI Options](#cli-options)
- [Environment Variables](#environment-variables)
- [conftest.py](#conftestpy)

## Config File Types & Precedence

Checked in order (first match wins):

1. **pytest.toml / .pytest.toml** (v9.0+) -- highest precedence, `[pytest]` section
2. **pytest.ini / .pytest.ini** -- INI syntax, matches even when empty
3. **pyproject.toml** (v6.0+) -- `[tool.pytest]` (v9.0+) or `[tool.pytest.ini_options]` table
4. **tox.ini** -- requires `[pytest]` section
5. **setup.cfg** -- requires `[tool:pytest]` section (not recommended)

```toml
# pyproject.toml
[tool.pytest.ini_options]
addopts = "-ra -q --strict-markers"
testpaths = ["tests"]
markers = [
    "slow: marks tests as slow",
    "integration: integration tests",
]
```

```ini
# pytest.ini
[pytest]
addopts = -ra -q --strict-markers
testpaths = tests
```

## Root Directory Determination

1. Use `-c` flag path if provided
2. Find common ancestor of specified args
3. Search upward for config files
4. Fall back to `setup.py`, then cwd

`config.rootpath` (pathlib.Path), `config.inipath` (pathlib.Path|None)

## INI Options

### Test Discovery
| Option | Default | Description |
|--------|---------|-------------|
| `testpaths` | cwd | Directories to search for tests |
| `python_files` | `test_*.py *_test.py` | Test file patterns |
| `python_classes` | `Test` | Test class prefixes |
| `python_functions` | `test` | Test function prefixes |
| `norecursedirs` | `.* build dist CVS _darcs {arch} *.egg venv` | Dirs to skip |

### Execution Control
| Option | Default | Description |
|--------|---------|-------------|
| `addopts` | (none) | Extra CLI args always appended |
| `minversion` | (none) | Minimum pytest version |
| `required_plugins` | (none) | Required plugins (e.g. `pytest-xdist>=2.0`) |
| `usefixtures` | (none) | Fixtures applied to all tests |
| `xfail_strict` | `false` | Default `strict` for xfail |
| `empty_parameter_set_mark` | `skip` | `skip`/`xfail`/`fail_at_collect` |

### Markers
| Option | Default | Description |
|--------|---------|-------------|
| `markers` | (none) | Register markers (linelist) |

### Warnings
| Option | Default | Description |
|--------|---------|-------------|
| `filterwarnings` | (none) | Warning filters (linelist) |

Format: `action:message_regex:category:module_regex:lineno`
```ini
filterwarnings =
    error
    ignore::DeprecationWarning
    ignore::PendingDeprecationWarning:mymodule
```

### Output & Reporting
| Option | Default | Description |
|--------|---------|-------------|
| `console_output_style` | `progress` | `classic`/`progress`/`count` |
| `verbosity_assertions` | (none) | Assertion verbosity level |
| `verbosity_test_cases` | (none) | Test case output verbosity |
| `truncation_limit_lines` | 10 | Truncation for long output (0=off) |
| `truncation_limit_chars` | 90 | Character truncation (0=off) |

### Logging
| Option | Default | Description |
|--------|---------|-------------|
| `log_cli` | `false` | Enable live log output |
| `log_cli_level` | (none) | CLI log minimum level |
| `log_cli_format` | see below | CLI log format string |
| `log_cli_date_format` | `%H:%M:%S` | CLI log date format |
| `log_level` | `WARNING` | Capture minimum level |
| `log_format` | `%(levelname)-8s %(name)s:%(filename)s:%(lineno)d %(message)s` | Capture format |
| `log_date_format` | `%H:%M:%S` | Capture date format |
| `log_file` | (none) | Log file path |
| `log_file_level` | (none) | File log level |
| `log_file_format` | (none) | File log format |
| `log_file_date_format` | (none) | File log date format |
| `log_auto_indent` | `false` | Auto-indent multiline messages |

### Doctest
| Option | Default | Description |
|--------|---------|-------------|
| `doctest_encoding` | `utf-8` | Doctest file encoding |
| `doctest_optionflags` | (none) | `NORMALIZE_WHITESPACE ELLIPSIS` etc. |

Custom: `ALLOW_UNICODE`, `ALLOW_BYTES`, `NUMBER` (float precision matching).

### Temporary Files
| Option | Default | Description |
|--------|---------|-------------|
| `tmp_path_retention_count` | `3` | Sessions to retain tmp dirs |
| `tmp_path_retention_policy` | `all` | `all`/`failed`/`none` |

### JUnit XML
| Option | Default | Description |
|--------|---------|-------------|
| `junit_suite_name` | `pytest` | Suite name |
| `junit_family` | `xunit2` | `xunit1`/`xunit2` |
| `junit_duration_report` | `total` | `total`/`call` |
| `junit_logging` | `no` | `no`/`log`/`system-out`/`system-err`/`out-err`/`all` |
| `junit_log_passing_tests` | `true` | Log passing test output |

### Other
| Option | Default | Description |
|--------|---------|-------------|
| `cache_dir` | `.pytest_cache` | Cache directory path |
| `confcutdir` | (none) | Only load conftest at/below this dir |
| `faulthandler_timeout` | `0` | Timeout for faulthandler (0=disabled) |
| `pythonpath` | (none) | Dirs to add to sys.path |

## CLI Options

### Test Selection
```
pytest path/to/tests                    # run tests in path
pytest -k "EXPRESSION"                  # keyword filter (and/or/not)
pytest -m "MARKEXPR"                    # marker filter
pytest test_mod.py::TestClass::test_fn  # node ID
pytest test_mod.py::test_fn[param]      # parametrized variant
pytest --pyargs pkg.testing             # by package
pytest @tests_to_run.txt               # from file (v8.2+)
pytest --co / --collect-only            # collect without running
pytest --ignore=path                    # ignore during collection
pytest --deselect=nodeid                # deselect specific test
```

### Execution Control
```
pytest -x / --exitfirst                 # stop on first failure
pytest --maxfail=N                      # stop after N failures
pytest -s / --capture=no                # disable capture
pytest --capture={fd,sys,no,tee-sys}    # capture method
pytest --lf / --last-failed             # rerun failures only
pytest --ff / --failed-first            # failures first
pytest --nf / --new-first               # new tests first
pytest --sw / --stepwise                # stop on fail, resume next run
pytest --sw-skip                        # skip first failure in stepwise
pytest --import-mode={prepend,append,importlib}
```

### Output
```
pytest -v / --verbose                   # verbose output
pytest -q / --quiet                     # quiet output
pytest -r chars                         # summary: f E s x X p P a A N
pytest --tb={auto,long,short,line,native,no}
pytest -l / --showlocals               # locals in tracebacks
pytest --color={yes,no,auto}
pytest --no-header                      # suppress header
pytest --durations=N                    # N slowest (0=all)
pytest --durations-min=N                # minimum seconds threshold
```

### Debugging
```
pytest --pdb                            # PDB on failure
pytest --pdbcls=module:class            # custom debugger
pytest --trace                          # PDB at test start
pytest --setup-show                     # show fixture setup/teardown
pytest --setup-only / --setup-plan      # fixture info only
```

### Plugins
```
pytest -p NAME                          # load plugin
pytest -p no:NAME                       # disable plugin
pytest --disable-plugin-autoload        # disable all autoload
```

### Reporting
```
pytest --junit-xml=path                 # JUnit XML report
pytest --pastebin={failed,all}          # upload to bpaste
```

### Cache
```
pytest --cache-show [pattern]           # show cache
pytest --cache-clear                    # clear cache
pytest --lfnf={all,none}               # no-failures behavior
```

### Config
```
pytest --rootdir=path                   # force rootdir
pytest --override-ini=OPT=VAL          # override ini option
pytest -W FILTER                        # warning filter
pytest --basetemp=path                  # temp dir base
pytest --strict                         # strict-config + strict-markers
pytest --strict-markers                 # error on unknown markers
pytest --strict-config                  # error on unknown config
```

### Doctest
```
pytest --doctest-modules                # doctests in all modules
pytest --doctest-glob=PATTERN           # doctest file pattern
pytest --doctest-continue-on-failure
pytest --doctest-report={udiff,cdiff,ndiff,none}
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `PYTEST_ADDOPTS` | Extra CLI options (prepended) |
| `PYTEST_PLUGINS` | Comma-separated plugin modules to load |
| `PYTEST_CURRENT_TEST` | Set during execution to `nodeid (phase)` |
| `PYTEST_DEBUG` | Enable internal debug tracing |
| `PYTEST_THEME` | Pygments style for syntax highlighting |
| `PYTEST_THEME_MODE` | `light` or `dark` |
| `PY_COLORS`/`NO_COLOR`/`FORCE_COLOR` | Color control |
| `PYTEST_DISABLE_PLUGIN_AUTOLOAD` | Set to `1` to disable autoload |
| `PYTEST_DEBUG_TEMPROOT` | Override temp dir root |

## conftest.py

- Auto-discovered in test directories (not imported as regular modules)
- Fixtures defined are available to tests in same directory and below
- Multiple conftest.py files form hierarchy (inner takes precedence)
- Hook implementations in conftest affect tests in scope

Key uses:
- Define shared fixtures
- Implement hooks (`pytest_addoption`, `pytest_configure`, `pytest_collection_modifyitems`)
- Set `pytest_plugins = ["module1", "module2"]` to load plugins
- Define `collect_ignore`/`collect_ignore_glob` lists
- Call `pytest.register_assert_rewrite()`
