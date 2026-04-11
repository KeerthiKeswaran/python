import os
import importlib.util
import inspect
from minitest.core import TestResult

def discover_tests(path):
    tests = []
    fixtures = {}
    
    for root, _, files in os.walk(path):
        for file in files:
            if file.startswith("test_") and file.endswith(".py"):
                module_path = os.path.join(root, file)
                module_name = file[:-3]
                
                spec = importlib.util.spec_from_file_location(module_name, module_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                for name, obj in inspect.getmembers(module):
                    # Discovery via naming convention or decorator
                    if (name.startswith("test_") or hasattr(obj, "_is_test")) and inspect.isfunction(obj):
                        if hasattr(obj, "_parameterized_values"):
                            # Create individual test entries for each parameter set
                            arg_names = obj._parameterized_args
                            for vals in obj._parameterized_values:
                                if not isinstance(vals, (list, tuple)):
                                    vals = [vals]
                                params = dict(zip(arg_names, vals))
                                tests.append({
                                    "func": obj,
                                    "name": f"{name}[{','.join(f'{k}={v}' for k,v in params.items())}]",
                                    "module": module_name,
                                    "params": params,
                                    "skip": getattr(obj, "_is_skip", False),
                                    "skip_reason": getattr(obj, "_skip_reason", "")
                                })
                        else:
                            tests.append({
                                "func": obj, 
                                "name": name, 
                                "module": module_name, 
                                "params": {},
                                "skip": getattr(obj, "_is_skip", False),
                                "skip_reason": getattr(obj, "_skip_reason", "")
                            })
                    
                    # Discovery of fixtures
                    if hasattr(obj, "_is_fixture"):
                        fixtures[name] = {"func": obj, "scope": obj._fixture_scope}

    return tests, fixtures
