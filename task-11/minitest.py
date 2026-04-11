import argparse
import sys
import os
import time

# Add current dir and test dir to sys.path for test imports
sys.path.append(os.getcwd())

from minitest.discovery import discover_tests
from minitest.runner import TestRunner, print_summary

def main():
    parser = argparse.ArgumentParser(description="Minitest CLI")
    parser.add_argument("command", choices=["run"], help="Command to run")
    parser.add_argument("path", help="Path to tests directory")
    parser.add_argument("--parallel", type=int, default=1, help="Number of workers")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Ensure test path is in sys.path
    test_abs_path = os.path.abspath(args.path)
    if test_abs_path not in sys.path:
        sys.path.append(test_abs_path)
    
    if args.command == "run":
        print("=== Test Discovery ===")
        start_discovery = time.time()
        tests, fixtures = discover_tests(args.path)
        print(f"Found {len(tests)} tests across multiple modules")
        fixture_list = ", ".join([f"{name} ({info['scope']})" for name, info in fixtures.items()])
        print(f"Fixtures loaded: {fixture_list}")
        
        runner = TestRunner(parallel=args.parallel)
        start_execution = time.time()
        results = runner.run(tests, fixtures)
        total_time = time.time() - start_execution
        
        # Group by module for display
        current_module = None
        for r in results:
            if r.module != current_module:
                print(f"\n{args.path}/{r.module}.py")
                current_module = r.module
            
            status_symbol = r.status
            print(f"{status_symbol} {r.name}")
            if r.status != "PASS":
                print(f"  {r.error}")
            print(f"  [{r.duration:.2f}s]")
            
        print_summary(results, total_time)

if __name__ == "__main__":
    main()
