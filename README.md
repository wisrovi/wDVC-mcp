# wDVC MCP

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Ruff](https://img.shields.io/badge/style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![MCP](https://img.shields.io/badge/MCP-compatible-green.svg)](https://modelcontextprotocol.io/)

**wDVC MCP** — Model Context Protocol server for wDVC (DVC Data Pipeline Management).
Provides tools for architecting DVC pipelines, generating Docker worker commands for data download, and scaffolding wDVC projects.

## Features

| Feature | Description |
|---------|-------------|
| **Architect Blueprints** | Complete reference for DVC pipeline stages, worker queue, Gradio API, file downloader |
| **Docker Worker Command** | Generate exact `docker run` command for data download with configurable resources |
| **API Usage** | Gradio web UI examples for queue submission and status monitoring |
| **Pattern Catalog** | Searchable patterns from official/community repos with local fallbacks |
| **Project Scaffolding** | Generate complete wDVC project structure with templates |
| **Type Safety** | Fully typed, mypy clean |

## Installation

```bash
pip install wdvc-mcp
```

Or for development:

```bash
git clone https://github.com/wisrovi/wDVC-mcp.git
cd wDVC-mcp
pip install -e ".[dev]"
pre-commit install
```

## Quick Start

### Run the MCP Server

```bash
# Stdio transport (for Claude Desktop, etc.)
wdvc-mcp

# SSE transport (for HTTP clients)
wdvc-mcp --transport sse --port 8000
```

### Available Tools

| Tool | Description |
|------|-------------|
| `get_wdvc_architect_blueprints()` | Complete reference for all wDVC patterns |
| `get_wdvc_worker_command()` | Generate Docker run command for data download |
| `get_wdvc_api_usage()` | Gradio web UI usage examples |
| `search_wdvc_patterns(query)` | Search pattern catalog |

### Example: Get Docker Worker Command

```python
from wdvc_mcp.server import get_wdvc_worker_command

# Default command
cmd = get_wdvc_worker_command()
print(cmd)
```

**Output:**
```bash
mkdir -p ./projects

docker run -it --rm \
  --name worker \
  --hostname wDVC \
  --shm-size=16g \
  --cpus="4.0" \
  --memory="4g" \
  -e IP_HOST=192.168.1.84 \
  -e REDIS_HOST=192.168.10.108 \
  -v ./projects:/app/projects \
  -w /app \
  wisrovi/dataset-ia:worker-v1 \
  zsh
```

### Customize the Command

```python
cmd = get_wdvc_worker_command(
    ip_host="10.0.0.1",
    redis_host="10.0.0.2",
    projects_path="/data/my_projects",
    image="myorg/dataset-ia:latest",
    cpus="8.0",
    memory="16g",
    shm_size="32g",
)
```

## Project Scaffolding

Generate a complete wDVC project structure:

```python
from wdvc_mcp.templates import TemplateGenerator

bp = TemplateGenerator.get_files_blueprint("standard", "my_pipeline")
# bp contains: main.py, config/settings.py, worker/worker.py, api/api.py,
# dvc.yaml, Dockerfile.worker, docker-compose.worker.yaml, run_worker.sh, etc.
```

### Scaffold Types

| Type | Description | Folders |
|------|-------------|---------|
| `standard` | Full worker + API + config | config, worker, api, scripts, tests, .wdvc |
| `worker_service` | Worker only | config, worker, scripts, tests, .wdvc |
| `api_service` | API only | config, api, tests, .wdvc |
| `full_pipeline` | Everything + CI/CD | config, worker, api, scripts, pipeline, tests, examples, .wdvc, .github/workflows |

## Architecture

```
��─────────────────────────────────────────────────────────────��
│                      wDVC Architecture                       │
├─────────────────────────────────────────────────────────────��
│                                                              │
│  ��──────────────��    ��──────────────��    ��──────────────��  │
│  │  Gradio UI   │    │  Python SDK  │    │  MCP Tools   │  │
│  │  (api.py)    │    │  (worker.py) │    │  (server.py) │  │
│  └──────��───────��    └──────��───────��    └──────��───────��  │
│         │                   │                   │           │
│         └───────────────────��───────────────────��           │
│                             ��                                │
│                  ��─────────────────────��                    │
│                  │   Redis (wredis)    │                    │
│                  │  Queue + Hash +     │                    │
│                  │  SortedSet          │                    │
│                  └──────────��──────────��                    │
│                             │                                │
│         ��───────────────────��───────────────────��           │
│         ��                   ��                   ��           │
│  ��─────────────��    ��─────────────��    ��─────────────��    │
│  │ Docker      │    │ DVC Pipeline│    │ S3 Remote   │    │
│  │ Worker      │    │ (dvc.yaml)  │    │ (DVC push)  │    │
│  │ (container) │    │             │    │             │    │
│  └─────────────��    └─────────────��    └─────────────��    │
│                                                              │
��─────────────────────────────────────────────────────────────��
```

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
make test

# Run with coverage
make test-cov

# Lint & format
make lint
make format

# Type check
make typecheck

# Build package
make build

# Publish to PyPI
make publish
```

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `REDIS_HOST` | `localhost` | Redis server hostname |
| `REDIS_PORT` | `6379` | Redis server port |
| `REDIS_DB` | `0` | Redis database number |
| `REDIS_PASSWORD` | `None` | Redis password |
| `IP_HOST` | Auto-detected | Worker IP for registration |

### Docker Worker

The worker container requires:
- Redis accessible at `REDIS_HOST`
- Volume mount for `projects/` (contains DVC repo + data)
- Resources: 4 CPUs, 4GB RAM, 16GB SHM (configurable)

## Related Projects

- **wredis** - Redis control with Python (sync/async, decorators, HA)
- **wredis-mcp** - MCP server for wRedis architecting
- **wsqlite** - SQLite with Pydantic models
- **wsqlite-mcp** - MCP server for wSQLite
- **wpipe** - Pipeline orchestration
- **wpipe-mcp** - MCP server for wPipe

## License

MIT — see [LICENSE](LICENSE) for details.

---

*Generated by wDVC MCP by **wisrovi***