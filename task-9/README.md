# Plugin Architecture with Dynamic Module Loading

A professional-grade plugin system for Python applications, featuring discovery, dependency resolution, and lifecycle management.

## Features
- **Dynamic Discovery**: Scans local directories and system-installed entry points.
- **Topological Dependency Resolution**: Automatically calculates the correct activation order based on inter-plugin dependencies.
- **Lifecycle Management**: Standardized `activate()` and `deactivate()` hooks.
- **Robust Error Handling**: Detects circular dependencies and missing requirements.

## Project Structure
```text
task-9/
├── core/
│   ├── interface.py   # PluginBase definition
│   ├── manager.py     # PluginManager logic
│   └── main.py        # CLI entry point
├── internal_plugins/  # Built-in plugins
└── plugins/           # Third-party plugin directory
```

## How to Run
1. Navigate to the `task-9` directory.
2. Run the application:
   ```bash
   python core/main.py
   ```

## Example Plugins Included
- `markdown-parser`: Built-in core plugin.
- `dark-mode-theme`: Third-party theme.
- `rss-feed`: Third-party plugin depending on `markdown-parser`.
- `image-optimizer`: Third-party post-processor.

## Technical Stack
- `importlib` & `importlib.metadata`
- `abc.ABC` for interface enforcement
- `inspect` for dynamic class discovery
## Example Output
### Successful Activation (All dependencies met)
```text
=== Application Startup ===
$ sitegen build --theme dark-mode
[CORE] Scanning plugin directory: ./plugins/
[CORE] Discovered 4 plugins:
|-- dark-mode-theme v1.3.2 (third-party)
|-- image-optimizer v0.9.1 (third-party)
|-- markdown-parser v2.1.0 (built-in)
`-- rss-feed v1.0.0 (third-party, depends: markdown-parser)
[CORE] Resolving dependencies...
  markdown-parser (no dependencies) OK
  dark-mode-theme (no dependencies) OK
  image-optimizer (no dependencies) OK
  rss-feed -> markdown-parser OK (satisfied)
[CORE] Activating plugins in order...
[1/4] markdown-parser.activate() -> registered: .md -> HTML converter
[2/4] dark-mode-theme.activate() -> registered: theme "dark-mode"
[3/4] image-optimizer.activate() -> registered: post-processor for .png/.jpg
[4/4] rss-feed.activate() -> registered: command "generate-rss"
[CORE] Building site...
Processed 24 pages | Theme: dark-mode | RSS: feed.xml generated
Images optimized: 18 files, saved 4.2 MB
[CORE] Build complete -> ./dist/ (0.50s)
```

### Failed Activation (Missing dependency)
If a plugin requirement is missing, the system detects it before activation:
```text
=== Application Startup ===
$ sitegen build --theme dark-mode
[CORE] Scanning plugin directory: ./plugins/
[CORE] Discovered 3 plugins:
|-- dark-mode-theme v1.3.2 (third-party)
|-- image-optimizer v0.9.1 (third-party)
`-- rss-feed v1.0.0 (third-party, depends: markdown-parser)
[ERROR] Activation failed: Plugin 'rss-feed' depends on missing plugin 'markdown-parser'
[CORE] Building site...
Processed 24 pages | Theme: dark-mode | RSS: feed.xml generated
Images optimized: 18 files, saved 4.2 MB
[CORE] Build complete -> ./dist/ (0.50s)
```
