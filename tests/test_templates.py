"""Tests for wDVC MCP templates."""

import pytest

from wdvc_mcp.templates import TemplateGenerator


def test_get_supported_types():
    assert TemplateGenerator.get_supported_types() == [
        "standard",
        "worker_service",
        "api_service",
        "full_pipeline",
    ]


def test_get_folders_standard():
    folders = TemplateGenerator.get_folders("standard")
    assert "config" in folders
    assert "worker" in folders
    assert "api" in folders
    assert "scripts" in folders
    assert "tests" in folders
    assert ".wdvc" in folders


def test_get_folders_worker_service():
    folders = TemplateGenerator.get_folders("worker_service")
    assert "config" in folders
    assert "worker" in folders
    assert "scripts" in folders
    assert "tests" in folders
    assert ".wdvc" in folders
    assert "api" not in folders


def test_get_folders_api_service():
    folders = TemplateGenerator.get_folders("api_service")
    assert "config" in folders
    assert "api" in folders
    assert "tests" in folders
    assert ".wdvc" in folders
    assert "worker" not in folders


def test_get_folders_full_pipeline():
    folders = TemplateGenerator.get_folders("full_pipeline")
    assert "config" in folders
    assert "worker" in folders
    assert "api" in folders
    assert "scripts" in folders
    assert "pipeline" in folders
    assert "tests" in folders
    assert "examples" in folders
    assert ".wdvc" in folders
    assert ".github/workflows" in folders


def test_get_files_blueprint_standard_structure():
    bp = TemplateGenerator.get_files_blueprint("standard", "my_app")
    assert "main.py" in bp
    assert "config/settings.py" in bp
    assert "worker/worker.py" in bp
    assert "api/api.py" in bp
    assert "config/__init__.py" in bp
    assert "worker/__init__.py" in bp
    assert "api/__init__.py" in bp
    assert "requirements.txt" in bp
    assert "README.md" in bp
    assert "dvc.yaml" in bp
    assert "Dockerfile.worker" in bp
    assert "docker-compose.worker.yaml" in bp
    assert "run_worker.sh" in bp
    assert ".wdvc/config.json" in bp


def test_get_files_blueprint_project_name_interpolated():
    bp = TemplateGenerator.get_files_blueprint("standard", "order_service")
    assert "ORDER_SERVICE" in bp["README.md"]
    assert 'prefix="order_service"' in bp["cache/service.py"] if "cache/service.py" in bp else True


def test_get_files_blueprint_content_pieces():
    bp = TemplateGenerator.get_files_blueprint("standard", "app")
    settings = bp["config/settings.py"]
    assert "class RedisSettings" in settings
    assert "from_env" in settings

    worker = bp["worker/worker.py"]
    assert "class DVCQueueWorker" in worker
    assert "submit_task" in worker
    assert "process_task" in worker
    assert "start_worker" in worker
    assert "dvc:my_queue" in worker
    assert "dvc:my_set" in worker
    assert "redis" in worker.lower()

    api = bp["api/api.py"]
    assert "add_to_queue" in api
    assert "get_status" in api

    dvc_yaml = bp["dvc.yaml"]
    assert "stages:" in dvc_yaml
    assert "download:" in dvc_yaml
    assert "process:" in dvc_yaml
    assert "push:" in dvc_yaml

    dockerfile = bp["Dockerfile.worker"]
    assert "FROM wisrovi/agents:gpu-slim-dvc" in dockerfile
    assert "dvc add" in dockerfile or "dvc push" in dockerfile

    compose = bp["docker-compose.worker.yaml"]
    assert "services:" in compose
    assert "worker:" in compose
    assert "wisrovi/dataset-ia:worker-v1" in compose

    run_sh = bp["run_worker.sh"]
    assert "docker run -it --rm" in run_sh
    assert "IP_HOST" in run_sh
    assert "REDIS_HOST" in run_sh
    assert "wisrovi/dataset-ia:worker-v1" in run_sh

    main = bp["main.py"]
    assert "DVCQueueWorker" in main
    assert "run_worker" in main

    readme = bp["README.md"]
    assert "APP" in readme or "MY_APP" in readme or "app" in readme.lower()
    assert "docker run" in readme
    assert "IP_HOST" in readme
    assert "REDIS_HOST" in readme


def test_get_files_blueprint_worker_service():
    bp = TemplateGenerator.get_files_blueprint("worker_service", "app")
    assert "worker/worker.py" in bp
    assert "api/api.py" not in bp
    assert "main.py" in bp


def test_get_files_blueprint_api_service():
    bp = TemplateGenerator.get_files_blueprint("api_service", "app")
    assert "api/api.py" in bp
    assert "worker/worker.py" not in bp


def test_get_files_blueprint_full_pipeline_extra_scripts():
    bp = TemplateGenerator.get_files_blueprint("full_pipeline", "app")
    assert "scripts/download/download_some_file.py" in bp
    assert "scripts/process/process_data.py" in bp
    assert "scripts/upload/files_inventory.py" in bp
