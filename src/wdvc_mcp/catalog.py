"""Pattern catalog synchronization with local fallbacks for wDVC."""

import json
import logging
from contextlib import suppress
from urllib import request
from urllib.error import HTTPError, URLError

# Use a module-level logger
logger = logging.getLogger(__name__)


class PatternsCatalog:
    """Manages the synchronization of available wDVC patterns from the wisrovi SUITE.

    Synchronizes from GitHub just like the VS Code extension (with local fallbacks).
    """

    # URLs synchronized with the wisrovi ecosystem
    OFFICIAL_URL = "https://raw.githubusercontent.com/wisrovi/dataset-IA/main/patterns_catalog.json"
    COMMUNITY_URL = "https://raw.githubusercontent.com/wisrovi/dataset-IA-plugins/main/patterns_catalog.json"

    def __init__(self):
        """Initialize the catalog with hardcoded offline fallbacks."""
        self.cached_patterns = []
        self._load_initial_catalog()

    def _fetch_url(self, url: str) -> list:
        try:
            req = request.Request(url, headers={"User-Agent": "wdvc-mcp"})
            with request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    return json.loads(response.read().decode("utf-8"))
        except (URLError, HTTPError, TimeoutError, OSError) as e:
            logger.warning(f"Failed to fetch catalog from {url}: {e}")
        return []

    def refresh_catalog(self) -> list:
        """Fetch latest patterns from both official and community repositories."""
        official = self._fetch_url(self.OFFICIAL_URL)
        community = self._fetch_url(self.COMMUNITY_URL)

        # Merge and mark origin
        all_patterns = []
        for p in official:
            p["origin"] = "Official"
            all_patterns.append(p)
        for p in community:
            p["origin"] = "Community"
            all_patterns.append(p)

        if all_patterns:
            self.cached_patterns = all_patterns
            logger.info(f"Catalog refreshed: {len(self.cached_patterns)} patterns found.")

        return self.cached_patterns

    def search(self, query: str) -> list:
        """Filters cataloged patterns based on a search query keyword."""
        if not self.cached_patterns:
            self.refresh_catalog()

        query_lower = query.lower()
        results = []
        for pattern in self.cached_patterns:
            # Match against multiple fields
            fields = [
                pattern.get("name", ""),
                pattern.get("manager", ""),
                pattern.get("namespace", ""),
                pattern.get("module", ""),
                pattern.get("description", ""),
                pattern.get("category", ""),
            ]
            if any(query_lower in str(f).lower() for f in fields):
                results.append(pattern)
        return results

    def _load_initial_catalog(self):
        """Initial load with hardcoded fallbacks if offline."""
        self.cached_patterns = [
            {
                "name": "dvc_queue_worker",
                "manager": "DVCQueueWorker",
                "namespace": "wDVC.worker",
                "module": "worker",
                "description": "Background worker that processes DVC queue: clean, add, push, inventory",
                "category": "Data Processing",
                "origin": "Official",
            },
            {
                "name": "dvc_api_gradio",
                "manager": "Gradio API",
                "namespace": "wDVC.api",
                "module": "api",
                "description": "Web UI for submitting files to DVC queue and checking status",
                "category": "API",
                "origin": "Official",
            },
            {
                "name": "dvc_file_downloader",
                "manager": "DVCFileDownloader",
                "namespace": "wDVC.scripts.download",
                "module": "download_some_file",
                "description": "Download files from DVC S3 remote using boto3 with progress bar",
                "category": "Data Access",
                "origin": "Official",
            },
            {
                "name": "dvc_worker_queue",
                "manager": "RedisQueueManager",
                "namespace": "wDVC.queue",
                "module": "worker_queue",
                "description": "Redis-backed queue for DVC task processing with status tracking",
                "category": "Queue",
                "origin": "Official",
            },
            {
                "name": "docker_worker_run",
                "manager": "Docker Runner",
                "namespace": "wDVC.docker",
                "module": "docker-compose.worker",
                "description": "Run DVC worker in Docker with resource limits, DVC config, and project volume",
                "category": "Infrastructure",
                "origin": "Official",
            },
            {
                "name": "dvc_data_pipeline",
                "manager": "DVC Pipeline",
                "namespace": "wDVC.pipeline",
                "module": "dvc.yaml",
                "description": "DVC stages for data versioning, processing, and pushing to remote storage",
                "category": "Pipeline",
                "origin": "Official",
            },
        ]
        # Attempt an immediate refresh
        with suppress(Exception):
            self.refresh_catalog()
