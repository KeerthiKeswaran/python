import time
import traceback
import sys
import multiprocessing
import inspect
from minitest.core import TestResult, FixtureManager

def execute_single_test(test_info, fixtures_info):
    """Execution logic for a single test."""
    name = test_info["name"]
    module_name = test_info["module"]
    params = test_info["params"]
    
    import importlib
    mod = importlib.import_module(module_name)
    base_name = name.split('[')[0]
    func = getattr(mod, base_name)

    if test_info.get("skip"):
        return TestResult(name, module_name, "SKIP", error=test_info.get("skip_reason", ""))

    start_time = time.time()
    try:
        # Resolve fixtures
        sig = inspect.signature(func)
        kwargs = {**params}
        for param_name in sig.parameters:
            if param_name in fixtures_info and param_name not in kwargs:
                # Look up fixture in its module
                f_info = fixtures_info[param_name]
                f_mod = importlib.import_module(f_info["module"])
                f_func = getattr(f_mod, param_name)
                kwargs[param_name] = f_func()
        
        func(**kwargs)
        duration = time.time() - start_time
        return TestResult(name, module_name, "PASS", duration=duration)
    except AssertionError as e:
        duration = time.time() - start_time
        err_msg = str(e) or "Assertion failed"
        tb = traceback.extract_tb(sys.exc_info()[2])
        last_call = tb[-1] if tb else None
        loc = f"\n  at {last_call.filename}:{last_call.lineno}" if last_call else ""
        return TestResult(name, module_name, "FAIL", duration=duration, error=f"{err_msg}{loc}")
    except Exception as e:
        duration = time.time() - start_time
        return TestResult(name, module_name, "FAIL", duration=duration, error=str(e))

class TestRunner:
    def __init__(self, parallel=1):
        self.parallel = parallel

    def run(self, tests, fixtures):
        print(f"=== Execution ({self.parallel} workers) ===")
        
        # Prepare serializable test info
        serializable_tests = []
        for t in tests:
            st = t.copy()
            st.pop("func", None)
            serializable_tests.append(st)
        
        # Prepare serializable fixture info
        serializable_fixtures = {}
        for fn, info in fixtures.items():
            sf = info.copy()
            sf.pop("func", None)
            # We need to know which module the fixture is in
            sf["module"] = info["func"].__module__
            serializable_fixtures[fn] = sf

        if self.parallel > 1:
            with multiprocessing.Pool(self.parallel, initializer=self._init_worker, initargs=(sys.path,)) as pool:
                tasks = [(t, serializable_fixtures) for t in serializable_tests]
                results = pool.starmap(execute_single_test, tasks)
        else:
            # Re-wrap in a serializable way anyway for consistency or just pass original
            results = [execute_single_test(t, serializable_fixtures) for t in serializable_tests]
        
        return results

    @staticmethod
    def _init_worker(path):
        import sys
        sys.path[:] = path

def print_summary(results, total_time):
    passed = sum(1 for r in results if r.status == "PASS")
    failed = sum(1 for r in results if r.status == "FAIL")
    skipped = sum(1 for r in results if r.status == "SKIP")
    
    print("\n=== Summary ===")
    print(f"{len(results)} tests | {passed} passed | {failed} failed | {skipped} skipped")
    print(f"Total time: {total_time:.2f}s")
    
    if results:
        slowest = max(results, key=lambda r: r.duration)
        print(f"Slowest: {slowest.name} ({slowest.duration:.2f}s)")
