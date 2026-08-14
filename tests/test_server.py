"""Tests for wDVC MCP server."""

from unittest.mock import MagicMock, patch

import pytest

from wdvc_mcp.server import (
    WorkerCommandConfig,
    get_wdvc_api_usage,
    get_wdvc_architect_blueprints,
    get_wdvc_worker_command,
    search_wdvc_patterns,
)


def test_get_wdvc_architect_blueprints():
    """Test that blueprints returns all sections."""
    result = get_wdvc_architect_blueprints()
    assert isinstance(result, str)
    assert "DVC PIPELINE" in result
    assert "WORKER QUEUE" in result
    assert "GRADIO API" in result
    assert "FILE DOWNLOADER" in result
    assert "DOCKER WORKER COMMAND" in result
    assert "DOCKER COMPOSE" in result
    assert "WORKER LOGIC" in result
    assert "dvc.yaml" in result
    assert "wredis" in result


def test_get_wdvc_worker_command_defaults():
    """Test worker command with default parameters."""
    result = get_wdvc_worker_command()
    assert "mkdir -p ./projects" in result
    assert "docker run -it --rm" in result
    assert "--name worker" in result
    assert "--hostname wDVC" in result
    assert "--shm-size=16g" in result
    assert "--cpus=\"4.0\"" in result
    assert "--memory=\"4g\"" in result
    assert "-e IP_HOST=192.168.1.84" in result
    assert "-e REDIS_HOST=192.168.10.108" in result
    assert "-v ./projects:/app/projects" in result
    assert "-w /app" in result
    assert "wisrovi/dataset-ia:worker-v1" in result
    assert "zsh" in result


def test_get_wdvc_worker_command_custom():
    """Test worker command with custom parameters."""
    config = WorkerCommandConfig(
        ip_host="10.0.0.1",
        redis_host="10.0.0.2",
        projects_path="/data/projects",
        image="custom/image:latest",
        cpus="8.0",
        memory="16g",
        shm_size="32g",
    )
    result = get_wdvc_worker_command(config)
    assert "mkdir -p /data/projects" in result
    assert "-e IP_HOST=10.0.0.1" in result
    assert "-e REDIS_HOST=10.0.0.2" in result
    assert "-v /data/projects:/app/projects" in result
    assert "custom/image:latest" in result
    assert "--cpus=\"8.0\"" in result
    assert "--memory=\"16g\"" in result
    assert "--shm-size=32g" in result


def test_get_wdvc_api_usage():
    """Test API usage documentation."""
    result = get_wdvc_api_usage()
    assert "add_to_queue" in result
    assert "get_status" in result
    assert "dvc:my_queue" in result
    assert "dvc:my_set" in result
    assert "dvc:ticket:" in result
    assert "worker:" in result


def test_search_wdvc_patterns():
    """Test pattern catalog search."""
    with patch("wdvc_mcp.server.get_catalog") as mock_catalog:
        mock_instance = MagicMock()
        mock_instance.search.return_value = [
            {"name": "test_pattern", "manager": "TestManager", "description": "Test"}
        ]
        mock_catalog.return_value = mock_instance

        result = search_wdvc_patterns("worker")
        assert "test_pattern" in result
        mock_instance.search.assert_called_once_with("worker")
