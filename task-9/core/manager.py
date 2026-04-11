import os
import sys
import importlib.util
import inspect
from typing import Dict, List, Set, Type, Optional
from core.interface import PluginBase

class PluginManager:
    def __init__(self, plugin_dirs: List[str]):
        self.plugin_dirs = plugin_dirs
        self.discovered_plugins: Dict[str, PluginBase] = {}
        self.active_plugins: List[PluginBase] = []
        self.plugin_metadata: Dict[str, dict] = {}

    def discover(self):
        """Scans directories and entry points for plugins and loads them."""
        # 1. Scan filesystem directories
        for directory in self.plugin_dirs:
            if not os.path.exists(directory):
                continue
            
            for item in os.listdir(directory):
                plugin_path = os.path.join(directory, item)
                if os.path.isdir(plugin_path) and not item.startswith("__"):
                    self._load_plugin_from_dir(plugin_path, is_builtin=("internal" in directory))

        # 2. Discover via entry points (simulated or real)
        try:
            from importlib.metadata import entry_points
            # In Python 3.10+, entry_points() returns an EntryPoints object
            # We look for entry points in group 'sitegen.plugins'
            eps = entry_points(group='sitegen.plugins')
            for ep in eps:
                plugin_class = ep.load()
                if inspect.isclass(plugin_class) and issubclass(plugin_class, PluginBase):
                    plugin_instance = plugin_class()
                    self.discovered_plugins[plugin_instance.name] = plugin_instance
                    self.plugin_metadata[plugin_instance.name] = {
                        "version": plugin_instance.version,
                        "type": "installed",
                        "dependencies": plugin_instance.dependencies
                    }
        except (ImportError, Exception):
            pass

    def _load_plugin_from_dir(self, directory: str, is_builtin: bool = False):
        """Loads a plugin module from a specific directory."""
        module_name = os.path.basename(directory)
        plugin_file = os.path.join(directory, "plugin.py")
        
        if not os.path.exists(plugin_file):
            return

        try:
            # Dynamic loading
            spec = importlib.util.spec_from_file_location(module_name, plugin_file)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                # Sandboxed-ish: adding to sys.modules but keeping it isolated in scope
                sys.modules[module_name] = module
                spec.loader.exec_module(module)

                # Find PluginBase implementation
                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj) and issubclass(obj, PluginBase) and obj is not PluginBase:
                        plugin_instance = obj()
                        self.discovered_plugins[plugin_instance.name] = plugin_instance
                        self.plugin_metadata[plugin_instance.name] = {
                            "version": plugin_instance.version,
                            "type": "built-in" if is_builtin else "third-party",
                            "dependencies": plugin_instance.dependencies
                        }
        except Exception as e:
            print(f"[ERROR] Failed to load plugin from {directory}: {e}")

    def resolve_dependencies(self) -> List[str]:
        """Performs a topological sort to resolve plugin activation order."""
        graph = {name: plugin.dependencies for name, plugin in self.discovered_plugins.items()}
        sorted_plugins = []
        visited = set()
        temp_stack = set()

        def visit(node):
            if node in temp_stack:
                raise Exception(f"Circular dependency detected involving {node}")
            if node not in visited:
                temp_stack.add(node)
                for neighbor in graph.get(node, []):
                    if neighbor not in self.discovered_plugins:
                        raise Exception(f"Plugin '{node}' depends on missing plugin '{neighbor}'")
                    visit(neighbor)
                temp_stack.remove(node)
                visited.add(node)
                sorted_plugins.append(node)

        for name in graph:
            if name not in visited:
                visit(name)
        
        return sorted_plugins

    def activate_plugins(self):
        """Activates discovered plugins in the resolved dependency order."""
        try:
            activation_order = self.resolve_dependencies()
            print("[CORE] Resolving dependencies...")
            
            for name in self.discovered_plugins:
                meta = self.plugin_metadata[name]
                deps = meta['dependencies']
                if not deps:
                    print(f"  {name} (no dependencies) OK")
                else:
                    dep_str = ", ".join(deps)
                    print(f"  {name} -> {dep_str} OK (satisfied)")

            print("[CORE] Activating plugins in order...")
            for i, name in enumerate(activation_order, 1):
                plugin = self.discovered_plugins[name]
                print(f"[{i}/{len(activation_order)}] {name}.activate() -> ", end="")
                plugin.activate()
                self.active_plugins.append(plugin)
        except Exception as e:
            print(f"[ERROR] Activation failed: {e}")

    def shutdown(self):
        """Deactivates all plugins in reverse order."""
        for plugin in reversed(self.active_plugins):
            plugin.deactivate()
