"""Tests for wDVC MCP catalog."""

from unittest.mock import MagicMock, patch

import pytest

from wdvc_mcp.catalog import PatternsCatalog


@pytest.fixture
def catalog():
    with patch.object(PatternsCatalog, "refresh_catalog", return_value=[]):
        return PatternsCatalog()


def test_catalog_initialization(catalog):
    """Test catalog initializes with fallback patterns."""
    assert len(catalog.cached_patterns) > 0
    # Check for key patterns
    names = [p["name"] for p in catalog.cached_patterns]
    assert "dvc_queue_worker" in names
    assert "dvc_api_gradio" in names
    assert "dvc_file_downloader" in names
    assert "dvc_worker_queue" in names
    assert "docker_worker_run" in names
    assert "dvc_data_pipeline" in names


def test_catalog_pattern_structure(catalog):
    """Test each pattern has required fields."""
    for pattern in catalog.cached_patterns:
        assert "name" in pattern
        assert "manager" in pattern
        assert "namespace" in pattern
        assert "module" in pattern
        assert "description" in pattern
        assert "category" in pattern
        assert "origin" in pattern


def test_search_matches_name(catalog):
    """Test search matches pattern name."""
    results = catalog.search("queue")
    assert len(results) > 0
    assert any("queue" in p["name"].lower() for p in results)


def test_search_matches_manager(catalog):
    """Test search matches manager."""
    results = catalog.search("RedisQueueManager")
    assert len(results) > 0
    assert any("RedisQueueManager" in p["manager"] for p in results)


def test_search_matches_description(catalog):
    """Test search matches description."""
    results = catalog.search("docker")
    assert len(results) > 0
    assert any("docker" in p["description"].lower() for p in results)


def test_search_case_insensitive(catalog):
    """Test search is case insensitive."""
    results_lower = catalog.search("DOCKER")
    results_upper = catalog.search("docker")
    assert len(results_lower) == len(results_upper)


def test_search_no_results(catalog):
    """Test search with no matches returns empty list."""
    results = catalog.search("nonexistentpatternxyz")
    assert results == []


def test_refresh_catalog(monkeypatch):
    """Test catalog refresh fetches from URLs."""
    mock_patterns = [
        {"name": "remote_pattern", "manager": "RemoteManager", "origin": "Official"}
    ]

    def mock_fetch_url(url):
        if "wisrovi/dataset-IA" in url:
            return mock_patterns
        return []

    with patch("wdvc_mcp.catalog.request.urlopen") as mock_urlopen:
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = b'[{"name": "remote_pattern", "manager": "RemoteManager"}]'
        mock_response.__enter__ = lambda s: mock_response
        mock_response.__exit__ = lambda s, *a: None
        mock_urlopen.return_value = mock_response

        cat = PatternsCatalog()
        cat.cached_patterns = []  # Clear initial
        cat.refresh_catalog()

    assert any(p["name"] == "remote_pattern" for p in cat.cached_patterns)
