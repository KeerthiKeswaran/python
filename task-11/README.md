# Minitest: A Professional-Grade Miniature Testing Framework

A custom-built Python testing framework featuring discovery, fixtures, parameterization, and parallel execution logic.

## Features
- **Auto-Discovery**: Automatically finds tests in files matching `test_*.py`.
- **Flexible Fixtures**: Supports session and function-scoped fixtures via `@fixture`.
- **Parameterization**: Run a single test logic across multiple datasets with `@parameterize`.
- **Parallel Execution**: Leverages `multiprocessing` to run tests in parallel, significantly reducing execution time for large suites.
- **Assertion Introspection**: Provides detailed failure reports including file name and line number.
- **Skip Support**: Easily skip tests with `@skip`.

## Installation
No external dependencies required! Minitest uses Python's standard library exclusively. 

## Usage
Run tests in a specific directory:
```bash
python minitest.py run tests/
```

Run tests in parallel (e.g., 4 workers):
```bash
python minitest.py run tests/ --parallel 4 --verbose
```

## Decoration Examples
```python
from minitest.core import test, fixture, parameterize

@fixture(scope="session")
def db():
    return Database()

@parameterize("val", [1, 2, 3])
def test_values(val, db):
    assert val in db.get_ids()
```

## Project Structure
```text
task-11/
├── minitest/
│   ├── core.py       # Decorators & Fixtures
│   ├── discovery.py  # Test discovery logic
│   └── runner.py     # Parallel execution engine
├── tests/            # Your test suite
└── minitest.py       # CLI Entry point
```

## Example Output
```text
$ python minitest.py run tests --parallel 4 --verbose
=== Test Discovery ===
Found 8 tests across multiple modules
Fixtures loaded: db_connection (session), temp_dir (function)
=== Execution (4 workers) ===

tests/test_auth.py
FAIL test_login_expired_token
  Expected status=401, got status=200
  at C:\Users\keshw\Downloads\Presidio\Internship\Tasks\4-Python\task-11\tests\test_auth.py:21
  [0.00s]
PASS test_login_invalid_password
  [0.00s]
PASS test_login_valid_credentials
  [0.00s]

tests/test_cart.py
PASS test_add_item[product_id=1,qty=1]
  [0.00s]
PASS test_add_item[product_id=2,qty=5]
  [0.00s]
PASS test_add_item[product_id=99,qty=0]
  [0.00s]
SKIP test_checkout_stripe
  skipped: no API key
  [0.00s]
PASS test_full_integration
  [0.20s]

=== Summary ===
8 tests | 6 passed | 1 failed | 1 skipped
Total time: 0.61s
Slowest: test_full_integration (0.20s)
```
