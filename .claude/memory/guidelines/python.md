# Python Coding Guidelines

Focuses on modern Python patterns and common AI agent mistakes that ruff cannot auto-fix.

## Core Standards

- **Type Annotations**: All function parameters and return types must be annotated
- **Union Syntax**: Use PEP 604 syntax (`str | None`, `int | str`) instead of `Optional`/`Union`
- **Modern Features**: Use Python 3.10+ features where appropriate

```bash
# Run static analysis
ruff check --fix .
ruff format .
pyright
```

## Package Structure

### Always Create `__init__.py` (INP001)

**Always include `__init__.py` in Python package directories.** Per Ruff INP001,
a missing `__init__.py` is typically an oversight. Namespace packages (PEP 420)
are rarely needed.

```python
# Good - Package with __init__.py
src/
└── mypackage/
    ├── __init__.py      # Required - marks directory as package
    ├── core.py
    └── utils.py

# Good - API exposure in __init__.py
from .core import MainClass
from .utils import helper_function
__all__ = ["MainClass", "helper_function"]

# Good - Empty __init__.py is acceptable
# (just create the file, can be empty)
```

### No sys.path Manipulation

**Never use `sys.path.insert()` to add source directories.** Use proper package installation instead:

```python
# Bad - Manual sys.path manipulation
import sys
sys.path.insert(0, "src")  # Don't do this
import mtnmai

# Good - Use modern uv workflow
# Run: uv sync (installs dependencies and editable package)
import mtnmai  # Works with proper uv project setup
```

**Proper solutions:**

- **Modern uv workflow**: `uv sync` (recommended for uv-managed projects)
- **Legacy editable install**: `pip install -e .` (only if not using uv)
- **Environment variables**: Set PYTHONPATH for development (not recommended)
- **Package structure**: Follow standard `src/` layout with proper `pyproject.toml`

## Modern Type Syntax

```python
# Good - Use PEP 604 union syntax (Python 3.10+)
def process_data(data: dict | None) -> str | None:
    if data is None:
        return None
    return str(data)

# Good - Built-in generics (Python 3.9+)
def merge_lists(a: list[str], b: list[str]) -> list[str]:
    return a + b

# Good - Use datetime.UTC (Python 3.13+)
from datetime import datetime
import datetime as dt

def get_utc_time() -> datetime:
    return datetime.now(dt.UTC)  # Modern UTC alias

# Bad - Old typing syntax
from typing import Optional, Union, List
def process_data(data: Optional[dict]) -> Union[str, None]:
    pass
def merge_lists(a: List[str], b: List[str]) -> List[str]:
    pass

# Bad - Old timezone syntax (UP017)
import datetime
def get_utc_time() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)  # Use datetime.UTC instead
```

## Import Conventions

### Top-Level Imports (PLC0415)

```python
# Good - All imports at module top
import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

def process_data():
    return datetime.datetime.now()

# Bad - Import inside function (except for lazy loading)
def process_data():
    import datetime  # Should be at module top
    return datetime.datetime.now()
```

## Module Shadowing

```python
# Bad - Don't shadow standard library
import json
json = {"key": "value"}  # Now shadows the json module

dict = {}  # Shadows built-in dict
collections = []  # Shadows collections module
```

## Critical Function Design

### No Mutable Defaults (B006)

```python
# Good - Avoid mutable defaults
def add_item(item: str, items: list[str] | None = None) -> list[str]:
    if items is None:
        items = []
    return items + [item]

# Bad - Mutable default argument
def add_item(item: str, items: list[str] = []) -> list[str]:
    items.append(item)
    return items
```

### Unused Arguments

```python
# Good - Prefix unused arguments with underscore
def event_handler(_event_type: str, data: dict) -> None:
    """Handle event. Event type required by interface but not used."""
    process_data(data)
```

## Security

### No Assert in Production (S101)

```python
# Good - Proper exceptions for validation
def validate_data(data: dict) -> None:
    if not data:
        raise RuntimeError("Data cannot be empty")

# Bad - Assert statements disabled in production
def validate_data(data: dict) -> None:
    assert data, "Data cannot be empty"
```

### Logic Errors

```python
# Bad - Assert tuple (always True)
def validate_config(config: dict) -> None:
    assert ("api_key" in config, "API key is required")  # Tuple always True!

# Bad - If tuple (always True) 
def process_data(data: dict | None) -> str:
    if (data, "checking data"):  # Tuple always True!
        return json.dumps(data)
    return "{}"
```

### Prohibited Functions

```python
# NEVER use - Security vulnerabilities
eval(user_input)  # Arbitrary code execution
exec(user_code)   # Arbitrary code execution
yaml.load(data)   # Unsafe deserialization
pickle.load(file)  # Dangerous deserialization
subprocess.call(cmd, shell=True)  # Shell injection

# Use safe alternatives
ast.literal_eval(safe_input)
yaml.safe_load(data)
subprocess.run(["cmd", "arg"], shell=False)
```

## Logging

### Exception Handling Patterns

#### Logging Hierarchy Principle

**CRITICAL: Use `logger.exception()` ONLY at the outermost layer (entry points).** Inner functions should simply `raise` or use exception chaining. This prevents duplicate error logging in call chains.

**Three-Layer Architecture:**

```python
from loguru import logger

# Layer 1: Outermost (Entry Point) - ONLY place for logger.exception()
def run_workflow(config: dict) -> dict:
    """Workflow entry point."""
    try:
        return process_workflow(config)
    except Exception:
        logger.exception("Workflow execution failed")  # Log ONCE here
        raise

# Layer 2: Middle (Business Logic) - Use raise or exception chaining
def process_workflow(config: dict) -> dict:
    """Business logic layer."""
    validated = validate_config(config)  # May raise
    return execute_steps(validated)  # May raise

# Layer 3: Inner (Utilities) - Use raise only
def validate_config(config: dict) -> dict:
    """Utility layer."""
    if not config:
        raise ValueError("Config cannot be empty")
    return config
```

**Layer responsibilities:**

- **Outermost** (workflows, APIs, CLI): Log with `logger.exception()`, handle recovery
- **Middle** (business logic): Propagate with `raise` or add context with `raise ... from e`
- **Inner** (utilities): Propagate with `raise` only, no logging

#### Standard Patterns

##### Pattern 1: Log and Re-raise (Outermost Layer)

Use when you need error visibility but want the exception to propagate.

```python
def run_workflow(config: dict) -> dict:
    try:
        return process_workflow(config)
    except Exception:
        logger.exception("Workflow execution failed")
        raise
```

##### Pattern 2: Error Recovery (Outermost Layer)

###### Variant A: Return Default Value

```python
def fetch_optional_data(url: str) -> dict | None:
    try:
        return make_request(url)
    except Exception:
        logger.exception("Optional data fetch failed")
        return None
```

###### Variant B: API Response with Trace ID

```python
import uuid

def process_request(request_data: dict) -> Response:
    try:
        result = process_data(request_data)
        return Response(data=result, status=Status.SUCCESS)
    except Exception as e:
        trace_id = uuid.uuid4().hex[:8]
        logger.exception(f"Request failed (trace_id={trace_id})")
        return Response(
            data=[],
            status=Status.FAILED,
            message=f"Error ({type(e).__name__}): {e} [trace_id={trace_id}]",
        )
```

##### Pattern 3: Exception Chaining (Any Layer)

Add context while preserving the original exception.

```python
# Middle layer: Add context
def initialize_service(config: dict) -> None:
    try:
        connect_to_database(config)
    except Exception as e:
        raise RuntimeError("Service initialization failed") from e

# Outermost layer: Log the chained exception
def main() -> None:
    try:
        initialize_service(load_config())
    except Exception:
        logger.exception("Application startup failed")  # Logs full chain
        raise
```

##### Pattern 4: Specific Exception Types

###### A. Handle Specific Exceptions Differently

```python
try:
    with config_path.open() as f:
        data = json.load(f)
    return validate_config(data)
except FileNotFoundError:
    logger.error(f"Config file not found: {config_path}")
    raise
except json.JSONDecodeError as e:
    raise ValueError(f"Invalid JSON in {config_path}") from e
except ValidationError as e:
    raise ValueError(f"Invalid config in {config_path}") from e
except Exception as e:
    raise RuntimeError(f"Unexpected error loading {config_path}") from e
```

###### B. Multiple Exceptions with Same Handling

```python
# Handle related exceptions together
try:
    value = parse_and_validate(input_str)
except (TypeError, ValueError) as e:
    raise ValueError(f"Invalid input format: {input_str}") from e

# Re-raise without wrapping
try:
    source = load_source(path)
except (KeyError, ValueError):
    raise  # Preserve original exception
```

###### C. Graceful Degradation (No Re-raise)

```python
# Non-critical errors: log warning and continue
for file_path in file_paths:
    try:
        process_file(file_path)
    except PermissionError:
        logger.warning(f"Permission denied, skipping: {file_path}")
        # Continue processing other files
```

###### D. Resource Cleanup with Finally

```python
resource = None
try:
    resource = acquire_resource()
    process(resource)
finally:
    if resource:
        try:
            cleanup(resource)
        except Exception:
            logger.exception("Cleanup failed")
```

#### Common Mistakes

```python
# Bad: Multiple logger.exception() calls create duplicate logs
# run_workflow() → logger.exception("Workflow failed")
#   ↓ calls process_data() → logger.exception("Processing failed")  # DUPLICATE!
#     ↓ calls transform() → logger.exception("Transform failed")    # DUPLICATE!
# Result: Same error logged 3 times!

# Good: Only log at the outermost layer
def run_workflow(config: dict) -> dict:
    try:
        return process_data(config)  # Inner functions just raise
    except Exception:
        logger.exception("Workflow failed")  # Log ONCE
        raise
```

#### Guidelines Summary

1. **One log per error** - Use `logger.exception()` only at outermost layer (entry points)
2. **Specific exceptions first** - Catch specific types before generic `Exception`
3. **Multiple exceptions** - Use `(ExceptionA, ExceptionB)` for same handling
4. **Exception chaining** - Use `raise ... from e` to preserve original exception and add context
5. **Inner functions** - Use `raise` only, never `logger.exception()`
6. **Resource cleanup** - Use `finally` with nested try-except for cleanup
7. **Stack traces** - `logger.exception()` captures full traces; `logger.error()` does not

### Module-Specific Logger (LOG015)

```python
import logging

# Good - Use module-specific logger
logger = logging.getLogger(__name__)

def process_data():
    logger.info("Processing data")

# Bad - Direct root logger usage
def process_data():
    logging.info("Processing data")  # Uses root logger
```

## File Operations

### Use Path.open() (PTH123)

```python
from pathlib import Path

# Good - Use Path.open() 
def read_config(config_path: Path) -> dict:
    with config_path.open(encoding="utf-8") as f:
        return json.load(f)

# Bad - Use builtin open()
def read_config(config_path: str) -> dict:
    with open(config_path) as f:
        return json.load(f)
```

## Performance

### List Operations

```python
# Good - Use extend() for performance (PERF401)
result = []
result.extend(process_item(item) for item in items)

# Bad - Inefficient append loop
tasks = []
for item in items:
    tasks.append(create_task(item))
```

### Async Patterns

#### No Blocking Calls in Async (ASYNC210)

```python
# Good - Non-blocking async operations
async def fetch_data(url: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()

# Bad - Blocking HTTP calls in async function
async def fetch_data_blocking(url: str) -> str:
    import requests  # Blocking HTTP library
    response = requests.get(url)  # Blocks event loop
    return response.text
```

#### Modern Concurrency with TaskGroup (Python 3.11+)

```python
# Good - TaskGroup for concurrent execution
async def fetch_multiple_items(urls: list[str]) -> dict[str, str]:
    results = {}
    async with asyncio.TaskGroup() as tg:
        tasks = {url: tg.create_task(fetch_data(url)) for url in urls}
    
    for url, task in tasks.items():
        try:
            results[url] = task.result()
        except Exception as e:
            logger.error("Failed to fetch %s: %s", url, e)
    
    return results

# Legacy - asyncio.gather (Python 3.7+)
async def fetch_multiple_items_legacy(urls: list[str]) -> list[str]:
    results = await asyncio.gather(
        *[fetch_data(url) for url in urls],
        return_exceptions=True
    )
    return [r for r in results if not isinstance(r, Exception)]
```

## Modern Python Patterns

### Match-Case with Literal (Python 3.10+)

```python
from typing import Literal

Status = Literal["active", "inactive", "pending"]

def handle_status(status: Status) -> str:
    match status:
        case "active":
            return "Process normally"
        case "inactive":
            return "Skip processing"
        case "pending":
            return "Queue for review"

# Avoid constant conditions
def bad_example() -> float:
    if True:  # Always True - dead code
        return 1.0
    return 0.0  # Never reached
```

### Avoid Global State (PLW0602)

```python
from dataclasses import dataclass
from typing import ClassVar

# Good - Use classes for state management
@dataclass(slots=True)
class Config:
    """Configuration with optimized memory usage."""
    max_size: float
    timeout: int
    
    DEFAULT_TIMEOUT: ClassVar[int] = 30

class Processor:
    def __init__(self, config: Config) -> None:
        self._config = config
        self._state: dict[str, float] = {}

# Bad - Global mutable state
STATE = {}  # Global mutable
def process_data(key: str) -> None:
    global STATE  # Avoid global state
    STATE[key] = 1.0
```

## Class Design

### BaseModel vs Dataclass

```python
# Good - BaseModel for I/O boundaries
class APIRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(pattern=r'^[^@]+@[^@]+\.[^@]+$')

# Good - Lightweight dataclass for internal logic
@dataclass(slots=True)
class User:
    name: str
    email: str
    
    def is_valid(self) -> bool:
        return bool(self.name and self.email)

# Bad - BaseModel for everything (unnecessary overhead)
class InternalData(BaseModel):
    name: str
    email: str
```

### Memory Optimization with **slots**

```python
# Good - String subclasses with __slots__ for memory efficiency
class Symbol(str):
    __slots__ = ()
    
    def __new__(cls, value: str) -> "Symbol":
        return super().__new__(cls, value.upper())

# Good - NamedTuple with __slots__
class Point(NamedTuple):
    __slots__ = ()
    x: float
    y: float

# Bad - Missing __slots__ in subclasses
class Symbol(str):
    def __new__(cls, value: str) -> "Symbol":
        return super().__new__(cls, value.upper())
```

## Testing

### pytest Exception Testing (PT010, PT011, PT012)

```python
import pytest

# Good - Specific exception testing
def test_invalid_calculation():
    with pytest.raises(ValueError, match="Cannot be negative"):
        calculate_value(-100)

# Bad - Vague or overly broad exception testing
def test_calculation_fails():
    with pytest.raises(Exception):  # Too broad
        calculate_value(-100)
    
    with pytest.raises():  # No exception specified
        calculate_value(-100)
```

### pytest Assertion Style (PT018)

```python
# Good - Simple, clear assertions
def test_calculations():
    result = calculate_interest(1000, 0.05)
    assert result > 1000
    assert result < 1100
    
    data = create_test_data()
    assert len(data) == 5
    assert data.is_valid()

# Bad - Complex composite assertions (hard to debug)
def test_calculations_complex():
    result = calculate_interest(1000, 0.05)
    assert result > 1000 and result < 1100 and isinstance(result, float)
```

## Code Simplification

### Use enumerate() (SIM113)

```python
# Good - Use enumerate for index-based iteration
def process_items(items: list[str]) -> list[dict]:
    result = []
    for index, item in enumerate(items):
        result.append({"index": index, "value": item})
    return result

# Bad - Manual index management
def process_items_manual(items: list[str]) -> list[dict]:
    result = []
    index = 0
    for item in items:
        result.append({"index": index, "value": item})
        index += 1  # Should use enumerate
    return result
```

### String Formatting

#### No Empty f-strings (F541)

```python
# Good - Use placeholders or regular strings
def format_message(name: str) -> str:
    return f"Hello, {name}!"  # Has placeholder

def get_header() -> str:
    return "Status Report"  # Regular string

# Bad - f-string without placeholders
def get_header() -> str:
    return f"Status Report"  # Unnecessary f-string
```

#### Set Comprehensions (C401)

```python
# Good - Use set comprehension for better performance
def get_unique_names(users: list[dict]) -> set[str]:
    return {user["name"] for user in users}

# Bad - Generator with set() wrapper
def get_unique_names(users: list[dict]) -> set[str]:
    return set(user["name"] for user in users)  # Unnecessary generator
```

## Summary

### Focus Areas for AI Agents

1. **Modern Type Syntax**: Use PEP 604 unions (`str | None`) and built-in generics (`list[str]`)
2. **Memory Optimization**: Use `@dataclass(slots=True)` and `__slots__` in subclasses
3. **Async Patterns**: Prefer `asyncio.TaskGroup` over `asyncio.gather`, avoid blocking calls
4. **Security**: No eval/exec/shell=True, use proper exceptions over asserts
5. **Performance**: Use `extend()` over loops, `enumerate()` over manual indexing, set comprehensions
6. **File Operations**: Use `Path.open()` instead of `open()`
7. **Exception Handling**: Use `logger.exception()` only at outermost layer; catch specific exceptions before generic `Exception`; use `(ExceptionA, ExceptionB)` for multiple exceptions; resource cleanup with `finally`
8. **Testing**: Specific pytest.raises() patterns, simple assertions
9. **Package Structure**: Always create `__init__.py` for packages (INP001),
   top-level imports only
10. **Class Design**: BaseModel for I/O boundaries, dataclass for internal logic
11. **String Formatting**: Use f-strings only with placeholders, regular strings otherwise
12. **DateTime**: Use `datetime.UTC` instead of `timezone.utc`

These guidelines focus on patterns that ruff cannot auto-fix and that AI agents commonly implement incorrectly.
