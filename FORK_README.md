# Strawberry GraphQL — Offline Fork

> This is a fork of [strawberry-graphql](https://github.com/strawberry-graphql/strawberry) (`v0.307.1`) modified for **air-gapped / offline environments** where the client browser has no internet access.

## What Changed

### Problem

The upstream Strawberry library loads GraphQL IDE assets (JavaScript, CSS) from external CDNs at runtime in the browser:
- **GraphiQL** → `unpkg.com` (React, ReactDOM, js-cookie, GraphiQL, Explorer plugin)
- **Pathfinder** → `esm.sh` (React, ReactDOM, Pathfinder IDE)
- **Apollo Sandbox** → `apollographql.com` (Embedded Sandbox bootstrap)

This means the GraphQL explorer **won't load** if the browser can't reach the internet.

### Solution

All external dependencies are **vendored locally** inside the library and served from the Strawberry server itself:

| Component | Change |
|---|---|
| `strawberry/static/vendor/` | **17 downloaded JS/CSS files** — all CDN assets stored locally |
| `strawberry/static/graphiql.html` | CDN URLs → local `/vendor/` paths |
| `strawberry/static/pathfinder.html` | CDN URLs → local `/vendor/` paths |
| `strawberry/static/apollo-sandbox.html` | CDN URL → local `/vendor/` path |
| `strawberry/cli/dev_server.py` | Mounts `/vendor` static files route |
| `strawberry/asgi/__init__.py` | Serves `/vendor/` files from ASGI app |
| `strawberry/vendor.py` | **NEW**: `mount_vendor_files()` utility for FastAPI/Starlette |
| `tests/http/test_graphql_ide.py` | Updated assertions for local paths |

### Limitations

- **Apollo Sandbox**: The vendored JS is a bootstrap that loads an iframe from Apollo's cloud. The initial script loads locally, but the IDE itself still requires internet. Use **GraphiQL** (default) or **Pathfinder** for fully offline operation.

---

## Quick Start

```bash
# Install with CLI support
pip install ".[cli]"

# Run the dev server
strawberry dev app

# Open in browser
# http://localhost:8000/graphql
```

---

## Framework Integration

The following frameworks serve vendor files **automatically** — no setup needed:
- ✅ **CLI dev server** (`strawberry dev app`)
- ✅ **ASGI / Starlette** (direct `GraphQL` app)
- ✅ **FastAPI** (`GraphQLRouter` — auto-serves `/vendor/` files and rewrites paths)

Other frameworks need a manual one-time setup:

### Django

Add a URL pattern in `urls.py`:

```python
import pathlib
from django.conf.urls.static import static

vendor_dir = pathlib.Path(__import__("strawberry").__file__).parent / "static" / "vendor"
urlpatterns += static("/vendor/", document_root=str(vendor_dir))
```

### Flask

```python
from flask import send_from_directory
import pathlib

vendor_dir = pathlib.Path(__import__("strawberry").__file__).parent / "static" / "vendor"

@app.route("/vendor/<path:filename>")
def serve_vendor(filename):
    return send_from_directory(str(vendor_dir), filename)
```

---

## Building a Wheel (.whl)

### Using Poetry (recommended)

```bash
# Install poetry if not available
pip install poetry

# Build the wheel
poetry build -f wheel

# The .whl file will be in dist/
ls dist/*.whl
# → dist/strawberry_graphql-0.307.1-py3-none-any.whl
```

### Using pip/build

```bash
# Install the build tool
pip install build

# Build the wheel
python -m build --wheel

# Output
ls dist/*.whl
```

### Using uv

```bash
# Build the wheel
uv build --wheel

# Output
ls dist/*.whl
```

### Installing the Built Wheel

```bash
# Install on another machine (with CLI extras)
pip install strawberry_graphql-0.307.1-py3-none-any.whl[cli]

# Or without CLI (library only)
pip install strawberry_graphql-0.307.1-py3-none-any.whl
```

### Verifying Vendor Files Are in the Wheel

```bash
# List wheel contents and check that vendor files are included
unzip -l dist/strawberry_graphql-*.whl | grep vendor
```

You should see entries like:
```
strawberry/static/vendor/react.production.min.js
strawberry/static/vendor/graphiql.min.js
strawberry/static/vendor/graphiql.min.css
...
```

---

## Vendored Dependencies

| File | Version | Source |
|---|---|---|
| `react.production.min.js` | 18.2.0 | unpkg.com |
| `react-dom.production.min.js` | 18.2.0 | unpkg.com |
| `js.cookie.min.js` | 3.0.5 | unpkg.com |
| `graphiql.min.js` | 3.8.3 | unpkg.com |
| `graphiql.min.css` | 3.8.3 | unpkg.com |
| `graphiql-plugin-explorer.umd.js` | 1.0.2 | unpkg.com |
| `graphiql-plugin-explorer.css` | 1.0.2 | unpkg.com |
| `react.esm.js` | 18.2.0 | esm.sh |
| `react-dom.esm.js` | 18.2.0 | esm.sh |
| `pathfinder-react.esm.js` | 0.2.6 | esm.sh |
| `pathfinder-style.css` | 0.2.6 | esm.sh |
| `node-process.mjs` | — | esm.sh |
| `node-buffer.mjs` | — | esm.sh |
| `node-events.mjs` | — | esm.sh |
| `node-tty.mjs` | — | esm.sh |
| `node-async_hooks.mjs` | — | esm.sh |
| `embeddable-sandbox.umd.production.min.js` | latest | apollographql.com |

---

## Modified Files Summary

```
strawberry/
├── asgi/__init__.py                          # Added _serve_vendor_file()
├── cli/dev_server.py                         # Added StaticFiles mount for /vendor
├── static/
│   ├── graphiql.html                         # Local vendor paths
│   ├── pathfinder.html                       # Local vendor paths
│   ├── apollo-sandbox.html                   # Local vendor path
│   └── vendor/                               # ← NEW: all vendored JS/CSS
│       ├── react.production.min.js
│       ├── graphiql.min.js
│       ├── ...
│       └── embeddable-sandbox.umd.production.min.js
tests/
└── http/test_graphql_ide.py                  # Updated assertions
```

---

## Upstream

Based on [strawberry-graphql v0.307.1](https://github.com/strawberry-graphql/strawberry).
Licensed under MIT. See [LICENSE](./LICENSE).
