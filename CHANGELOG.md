# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.1.0] - 2026-08-14

### Added

- **MCP Server** (`src/wdvc_mcp/server.py`) with FastMCP transport (stdio/SSE):
  - `get_wdvc_architect_blueprints()` - Complete reference for wDVC patterns (DVC pipeline, worker queue, Gradio API, file downloader, Docker worker command, Docker Compose, worker logic)
  - `get_wdvc_worker_command()` - Generates exact `docker run` command for data download with configurable IP_HOST, REDIS_HOST, projects path, image, resources
  - `get_wdvc_api_usage()` - Gradio web UI usage examples for queue management
  - `search_wdvc_patterns()` - Search pattern catalog by keyword

- **Pattern Catalog** (`src/wdvc_mcp/catalog.py`):
  - Official patterns from `wisrovi/dataset-IA` GitHub repo
  - Community patterns from `wisrovi/dataset-IA-plugins` GitHub repo
  - Local fallback patterns: DVC queue worker, Gradio API, file downloader, worker queue, Docker worker run, DVC data pipeline
  - Search across name, manager, namespace, module, description, category

- **Project Templates** (`src/wdvc_mcp/templates.py`):
  - Scaffold types: `standard`, `worker_service`, `api_service`, `full_pipeline`
  - Generated files: config/settings.py, worker/worker.py (DVCQueueWorker), api/api.py (Gradio), dvc.yaml, Dockerfile.worker, docker-compose.worker.yaml, run_worker.sh, main.py, requirements.txt, README.md
  - Template includes the exact `docker run` command for data download with placeholders

- **Tests** (`tests/`):
  - `test_server.py` - Blueprint content, worker command generation, API usage, pattern search
  - `test_catalog.py` - Initialization, pattern structure, search functionality, refresh
  - `test_templates.py` - Folder structure, blueprint content, project name interpolation, scaffold types

- **Developer Experience**:
  - `pyproject.toml` with dependencies (mcp, fastmcp, pydantic)
  - `Makefile` targets: install, test, test-cov, lint, format, typecheck, build, publish, clean
  - `.pre-commit-config.yaml` (ruff, black, pylint, mypy)
  - `.ruff.toml` (Google docstring convention)
  - `pylintrc` (customized for wDVC)
  - GitHub Actions CI workflow template in scaffolds

---

## [Unreleased]

### Planned

- Add `generate_wdvc_scaffold` MCP tool to create project structure programmatically
- Add `get_wdvc_docker_compose` tool for full stack deployment (API + Worker + Redis)
- Integration with wredis-mcp for shared Redis patterns
- Example projects in `examples/` directory
- Documentation site with Sphinx