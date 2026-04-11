import os
import sys
import time

# Add root to sys.path to allow core imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.manager import PluginManager

def main():
    print("=== Application Startup ===")
    print("$ sitegen build --theme dark-mode")
    
    internal_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "internal_plugins")
    plugins_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "plugins")
    
    print(f"[CORE] Scanning plugin directory: ./plugins/")
    
    manager = PluginManager([internal_dir, plugins_dir])
    manager.discover()
    
    print(f"[CORE] Discovered {len(manager.discovered_plugins)} plugins:")
    
    # Sort for consistent output appearance
    sorted_names = sorted(manager.discovered_plugins.keys())
    for i, name in enumerate(sorted_names):
        meta = manager.plugin_metadata[name]
        prefix = "|--" if i < len(sorted_names) - 1 else "`--"
        print(f"{prefix} {name} v{meta['version']} ({meta['type']}{', depends: ' + ', '.join(meta['dependencies']) if meta['dependencies'] else ''})")

    start_time = time.time()
    manager.activate_plugins()
    
    print("[CORE] Building site...")
    # Simulate work
    time.sleep(0.5)
    print("Processed 24 pages | Theme: dark-mode | RSS: feed.xml generated")
    print("Images optimized: 18 files, saved 4.2 MB")
    
    elapsed = time.time() - start_time
    print(f"[CORE] Build complete -> ./dist/ ({elapsed:.2f}s)")

if __name__ == "__main__":
    main()
