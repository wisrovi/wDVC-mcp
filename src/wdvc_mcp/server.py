"""MCP server, tools and CLI for wDVC architecting.

This server provides tools for:
- Getting architect blueprints for wDVC data structures and patterns
- Generating the exact Docker command to run the wDVC worker for data download
- Getting API usage examples for the Gradio web interface
- Scaffolding wDVC projects with proper structure
"""

import argparse
import json
import logging
import os
import signal
import subprocess
import sys
from dataclasses import dataclass
from functools import lru_cache
from typing import Optional

from mcp.server.fastmcp import FastMCP

from wdvc_mcp.catalog import PatternsCatalog
from wdvc_mcp.templates import TemplateGenerator

# Setup logging strictly to stderr to avoid breaking MCP protocol
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s", stream=sys.stderr)
logger = logging.getLogger(__name__)

# PID file for background service
PID_FILE = os.path.expanduser("~/.wdvc_mcp.pid")

# Create the primary FastMCP Server instance
mcp = FastMCP("wdvc-mcp-server")


@lru_cache(maxsize=1)
def get_catalog() -> PatternsCatalog:
    """Return the lazily-initialized shared catalog instance."""
    return PatternsCatalog()


# --- Tools ---


@mcp.tool()
def get_wdvc_architect_blueprints() -> str:
    """Complete reference with read/write/update examples for every wDVC data structure and pattern."""
    # 1. DVC Pipeline (dvc.yaml stages)
    pipeline_code = (
        "# wDVC Pipeline - Define stages in dvc.yaml\n"
        "# Location: dvc.yaml\n\n"
        "stages:\n"
        "  data_download:\n"
        "    cmd: python src/scripts/download/download_some_file.py ${FILE_PATH} --remote s3_remote\n"
        "    deps:\n"
        "      - .dvc/config\n"
        "    outs:\n"
        "      - data/raw/${FILE_PATH}:\n"
        "          cache: true\n\n"
        "  data_process:\n"
        "    cmd: python src/scripts/process/process_data.py data/raw/${FILE_PATH} data/processed/\n"
        "    deps:\n"
        "      - data/raw/${FILE_PATH}\n"
        "    outs:\n"
        "      - data/processed/:\n"
        "          cache: true\n\n"
        "  data_push:\n"
        "    cmd: dvc push data/processed/\n"
        "    deps:\n"
        "      - data/processed/\n"
    )

    # 2. Worker Queue (Redis-backed)
    worker_queue_code = (
        "# wDVC Worker Queue - Redis-backed task queue\n"
        "# Module: src/scripts/api/app/worker_queue.py\n\n"
        "from wdvc.worker_queue import (\n"
        "    put_in_queue,\n"
        "    get_Status_item,\n"
        "    get_complete_queue,\n"
        "    start_receiving,\n"
        "    register_worker_hash,\n"
        ")\n\n"
        "# PRODUCER: Submit file for DVC processing\n"
        'item = put_in_queue("/app/projects/data/raw/my_dataset")\n'
        "print(f'Task ID: {item[\"id\"]}')\n"
        "print(f'Queue position: {item[\"queue_size\"]}')\n\n"
        "# CONSUMER: Register worker function\n"
        "@queue_manager.on_message(\"dvc:my_queue\")\n"
        "def my_worker(message):\n"
        "    path = message[\"path\"]\n"
        "    # ... process with DVC ...\n"
        "    return results\n\n"
        "# Start consuming\n"
        "register_worker_hash(\"worker-v1\")\n"
        "start_receiving()\n"
    )

    # 3. Gradio API (Web UI)
    api_code = (
        "# wDVC Gradio API - Web interface for queue management\n"
        "# Module: api.py\n\n"
        "from api import add_to_queue, get_status\n\n"
        "# Add file to processing queue via web UI\n"
        'result = add_to_queue("/app/projects/data/raw/my_dataset")\n'
        "print(result)\n\n"
        "# Check status by Item ID\n"
        'status_data, html = get_status("DVC_abc123...")\n'
        "print(status_data)\n"
    )

    # 4. File Downloader (DVC S3 Remote)
    downloader_code = (
        "# wDVC File Downloader - Download from DVC S3 remote\n"
        "# Module: src/scripts/download/download_some_file.py\n\n"
        "from download_some_file import DVCFileDownloader, read_dvc_config, find_repo_root\n\n"
        "# Find repo root and read DVC config\n"
        "repo_root = find_repo_root()\n"
        "remote_config = read_dvc_config(repo_root / \".dvc/config\", remote_name=\"s3_remote\")\n\n"
        "# Initialize downloader\n"
        "downloader = DVCFileDownloader(remote_config)\n\n"
        "# Get URL and download\n"
        's3_url = downloader.get_dvc_file_url("val/data/file.xml", repo_path=str(repo_root))\n'
        "downloader.download_file(s3_url, Path(\"./downloads/data/file.xml\"))\n"
    )

    # 5. Docker Worker Command (THE KEY COMMAND FOR DATA DOWNLOAD)
    docker_worker_code = (
        "# wDVC Docker Worker - RUN THIS TO DOWNLOAD/PROCESS DATA\n"
        "# This command starts the DVC worker inside a container with all dependencies.\n"
        "# The worker pulls tasks from Redis queue and executes DVC pipeline.\n\n"
        "# 1. Create projects directory (mounted as volume)\n"
        "mkdir -p projects\n\n"
        "# 2. Run the worker container\n"
        "docker run -it --rm \\\n"
        "  --name worker \\\n"
        "  --hostname wDVC \\\n"
        "  --shm-size=16g \\\n"
        "  --cpus=\"4.0\" \\\n"
        "  --memory=\"4g\" \\\n"
        "  -e IP_HOST=192.168.1.84 \\\n"
        "  -e REDIS_HOST=192.168.10.108 \\\n"
        "  -v $(pwd)/projects:/app/projects \\\n"
        "  -w /app \\\n"
        "  wisrovi/dataset-ia:worker-v1 \\\n"
        "  zsh\n\n"
        "# INSIDE CONTAINER: Start the Python worker\n"
        "python worker.py\n\n"
        "# OR run directly with docker compose:\n"
        "# docker compose -f docker-compose.worker.yaml up worker\n"
    )

    # 6. Docker Compose (Production)
    docker_compose_code = (
        "# wDVC Docker Compose - Production deployment\n"
        "# File: docker-compose.worker.yaml\n\n"
        "services:\n"
        "  worker:\n"
        "    build:\n"
        "      context: .\n"
        "      dockerfile: Dockerfile.worker\n"
        "    image: wisrovi/dataset-ia:worker-v1\n"
        "    volumes:\n"
        "      - /mnt/dataset-ia/projects:/app/projects\n"
        "    deploy:\n"
        "      resources:\n"
        "        limits:\n"
        "          cpus: '4.0'\n"
        "          memory: 4g\n"
        "    hostname: wDVC\n"
        "    restart: always\n"
        "    environment:\n"
        "      - IP_HOST=192.168.1.84\n"
        "      - REDIS_HOST=192.168.10.108\n"
        "    logging:\n"
        "      driver: \"json-file\"\n"
        "      options:\n"
        "        max-size: \"50m\"\n"
        "        max-file: \"5\"\n"
    )

    # 7. Worker Processing Logic (worker.py)
    worker_logic_code = (
        "# wDVC Worker Logic - DVC Pipeline Execution\n"
        "# Module: worker.py\n\n"
        "from worker import worker_function\n"
        "from wdvc.worker_queue import get_from_queue, start_receiving, register_worker_hash\n\n"
        "# Register worker and start consuming\n"
        'register_worker_hash("version: 1.0.4")\n'
        "get_from_queue(worker_function)\n"
        "start_receiving()\n\n"
        "# The worker_function executes:\n"
        "# 1. CLEAN: rm -rf /app/.dvc/tmp && rm -rf /app/.dvc/cache\n"
        "# 2. ADD:   dvc add <path>\n"
        "# 3. PUSH:  dvc push <path>.dvc -v\n"
        "# 4. GIT:   git rm -r --cached <path> && git commit -m \"stop tracking\"\n"
        "# 5. INVENTORY: python /app/src/scripts/upload/files_inventory.py <path>\n"
    )

    return "\n\n".join([
        "=== wDVC Architect Blueprints ===\n",
        "# 1. DVC PIPELINE (dvc.yaml)",
        pipeline_code,
        "# 2. WORKER QUEUE (Redis + wredis)",
        worker_queue_code,
        "# 3. GRADIO API (Web UI)",
        api_code,
        "# 4. FILE DOWNLOADER (DVC S3 Remote)",
        downloader_code,
        "# 5. DOCKER WORKER COMMAND (DATA DOWNLOAD - USE THIS!)",
        docker_worker_code,
        "# 6. DOCKER COMPOSE (Production)",
        docker_compose_code,
        "# 7. WORKER LOGIC (worker.py)",
        worker_logic_code,
    ])


@dataclass
class WorkerCommandConfig:
    """Configuration for the Docker worker command."""
    ip_host: str = "192.168.1.84"
    redis_host: str = "192.168.10.108"
    projects_path: str = "./projects"
    image: str = "wisrovi/dataset-ia:worker-v1"
    cpus: str = "4.0"
    memory: str = "4g"
    shm_size: str = "16g"


# Module-level default config instance
DEFAULT_WORKER_CONFIG = WorkerCommandConfig()


@mcp.tool()
def get_wdvc_worker_command(config: WorkerCommandConfig | None = None) -> str:
    """Generate the exact Docker command to run the wDVC worker for data download/processing.

    This is THE command agents should use to start the worker that pulls data via DVC.
    The worker connects to Redis, consumes tasks from the queue, and executes DVC pipeline.

    Args:
        config: WorkerCommandConfig with IP, Redis host, projects path, image, and resource limits.

    Returns:
        Complete docker run command as a string.
    """
    if config is None:
        config = DEFAULT_WORKER_CONFIG
    # Ensure projects directory exists
    cmd = [
        f"mkdir -p {config.projects_path}",
        "",
        "docker run -it --rm \\",
        "  --name worker \\",
        "  --hostname wDVC \\",
        f"  --shm-size={config.shm_size} \\",
        f"  --cpus=\"{config.cpus}\" \\",
        f"  --memory=\"{config.memory}\" \\",
        f"  -e IP_HOST={config.ip_host} \\",
        f"  -e REDIS_HOST={config.redis_host} \\",
        f"  -v {config.projects_path}:/app/projects \\",
        "  -w /app \\",
        f"  {config.image} \\",
        "  zsh",
    ]
    return "\n".join(cmd)


@mcp.tool()
def get_wdvc_api_usage() -> str:
    """Get usage examples for the wDVC Gradio API (web interface for queue management)."""
    return (
        "# wDVC Gradio API Usage\n\n"
        "## Start the API Server\n"
        "python api.py\n"
        "# Opens at http://localhost:7860\n\n"
        "## Programmatic Usage\n"
        "from api import add_to_queue, get_status\n\n"
        "# Submit a file/directory for DVC processing\n"
        'result = add_to_queue("/app/projects/data/raw/my_dataset")\n'
        "# Returns HTML with task ID and queue position\n\n"
        "# Check status by Item ID\n"
        'status_data, html = get_status("DVC_abc123...")\n'
        "# status_data contains: id, path, status, metadata, timestamp\n\n"
        "## Queue Backend\n"
        "- Uses Redis via wredis (RedisQueueManager, RedisHashManager, RedisSortedSetManager)\n"
        "- Queue: dvc:my_queue\n"
        "- Sorted Set: dvc:my_set (tracks status: 0=pending, 1=processing, 2=completed, 3=failed)\n"
        "- Hash: dvc:ticket:<task_id> (stores full metadata)\n"
        "- Worker registration: worker:<IP_HOST>\n"
    )


@mcp.tool()
def search_wdvc_patterns(query: str) -> str:
    """Search the wDVC pattern catalog for relevant patterns.

    Args:
        query: Search keyword (e.g., 'worker', 'queue', 'docker', 'download', 'pipeline').

    Returns:
        JSON list of matching patterns with name, manager, description, category.
    """
    catalog = get_catalog()
    results = catalog.search(query)
    return json.dumps(results, indent=2)


# --- CLI Entry Point ---


def main() -> None:
    """CLI entry point for the wDVC MCP server."""
    parser = argparse.ArgumentParser(description="wDVC MCP Server")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse"],
        default="stdio",
        help="Transport protocol (default: stdio)",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port for SSE transport (default: 8000)",
    )
    args = parser.parse_args()

    if args.transport == "stdio":
        mcp.run(transport="stdio")
    elif args.transport == "sse":
        mcp.run(transport="sse")


if __name__ == "__main__":
    main()
