import functools
import inspect
from dataclasses import dataclass, field
from typing import Callable, List, Dict, Any, Optional

@dataclass
class TestResult:
    name: str
    module: str
    status: str # PASS, FAIL, SKIP
    duration: float = 0.0
    error: str = ""
    params: Dict[str, Any] = field(default_factory=dict)

class MinitestError(Exception):
    pass

def test(func):
    """Mark a function as a test."""
    func._is_test = True
    return func

def fixture(scope="function"):
    """Define a fixture."""
    def decorator(func):
        func._is_fixture = True
        func._fixture_scope = scope
        return func
    return decorator

def skip(reason):
    """Skip a test."""
    def decorator(func):
        func._is_skip = True
        func._skip_reason = reason
        return func
    return decorator

def parameterize(argnames: str, argvalues: List[Any]):
    """Parameterize a test."""
    def decorator(func):
        # We'll handle this in the discovery phase
        func._parameterized_args = argnames.split(',')
        func._parameterized_values = argvalues
        return func
    return decorator

class FixtureManager:
    def __init__(self):
        self.fixtures = {}
        self.cached_results = {}

    def register(self, name, func, scope):
        self.fixtures[name] = {"func": func, "scope": scope}

    def get_fixture_value(self, name, scope_id=None):
        if name not in self.fixtures:
            raise MinitestError(f"Fixture {name} not found")
        
        info = self.fixtures[name]
        scope = info["scope"]
        
        # Simple caching based on scope
        cache_key = (name, scope_id if scope != "session" else "global")
        if cache_key in self.cached_results:
            return self.cached_results[cache_key]
        
        value = info["func"]()
        self.cached_results[cache_key] = value
        return value
