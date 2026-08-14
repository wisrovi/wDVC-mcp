"""Advanced scaffolding templates for professional wDVC development."""


class TemplateGenerator:
    """Provides professional boilerplate for wDVC projects following wisrovi standards."""

    @staticmethod
    def get_supported_types() -> list[str]:
        """Return the list of supported scaffold types."""
        return ["standard", "worker_service", "api_service", "full_pipeline"]

    @staticmethod
    def get_folders(scaffold_type: str) -> list[str]:
        """Return the folder layout for the requested scaffold type."""
        if scaffold_type == "worker_service":
            return [
                "config",
                "worker",
                "scripts",
                "tests",
                ".wdvc",
            ]
        if scaffold_type == "api_service":
            return [
                "config",
                "api",
                "tests",
                ".wdvc",
            ]
        if scaffold_type == "full_pipeline":
            return [
                "config",
                "worker",
                "api",
                "scripts",
                "pipeline",
                "tests",
                "examples",
                ".wdvc",
                "scripts",
                ".github/workflows",
            ]
        return [
            "config",
            "worker",
            "api",
            "scripts",
            "tests",
            ".wdvc",
        ]

    @staticmethod
    def get_files_blueprint(scaffold_type: str, project_name: str = "wdvc_project") -> dict[str, str]:
        """Return filenames and their professional template content."""
        # Common settings
        settings_template = (
            "from dataclasses import dataclass\n\n"
            "@dataclass\n"
            "class RedisSettings:\n"
            '    """Centralized connection settings for wDVC Redis managers."""\n'
            '    host: str = "localhost"\n'
            "    port: int = 6379\n"
            "    db: int = 0\n"
            "    password: str | None = None\n"
            "    verbose: bool = False\n\n"
            "    @classmethod\n"
            '    def from_env(cls) -> "RedisSettings":\n'
            '        """Build settings from environment variables with sane defaults."""\n'
            "        import os\n"
            "        return cls(\n"
            '            host=os.getenv("REDIS_HOST", "localhost"),\n'
            '            port=int(os.getenv("REDIS_PORT", "6379")),\n'
            '            db=int(os.getenv("REDIS_DB", "0")),\n'
            '            password=os.getenv("REDIS_PASSWORD"),\n'
            "        )\n"
        )

        # Worker template
        worker_template = (
            "from wredis.queue import RedisQueueManager\n"
            "from wredis.hash import RedisHashManager\n"
            "from wredis.sortedset import RedisSortedSetManager\n"
            "from config.settings import RedisSettings\n"
            "from typing import Dict, Any\n\n\n"
            "class DVCQueueWorker:\n"
            '    """wDVC Queue Worker - processes DVC pipeline tasks from Redis queue."""\n\n'
            "    def __init__(self, settings: RedisSettings, poll_interval: int = 1):\n"
            "        self.queue_name = \"dvc:my_queue\"\n"
            "        self.set_name = \"dvc:my_set\"\n"
            "        self.queue_manager = RedisQueueManager(\n"
            "            host=settings.host,\n"
            "            port=settings.port,\n"
            "            db=settings.db,\n"
            "            poll_interval=poll_interval,\n"
            "            verbose=settings.verbose,\n"
            "        )\n"
            "        self.hash_manager = RedisHashManager(\n"
            "            host=settings.host,\n"
            "            port=settings.port,\n"
            "            db=settings.db,\n"
            "            verbose=settings.verbose,\n"
            "        )\n"
            "        self.sorted_set_manager = RedisSortedSetManager(\n"
            "            host=settings.host,\n"
            "            port=settings.port,\n"
            "            db=settings.db,\n"
            "            verbose=settings.verbose,\n"
            "        )\n\n"
            "    def submit_task(self, path: str) -> Dict[str, Any]:\n"
            '        """Submit a file/directory for DVC processing."""\n'
            "        import uuid\n"
            "        task_id = f\"DVC_{str(uuid.uuid4()).replace('-', '')}\"\n"
            "        queue_size = self.queue_manager.get_queue_length(self.queue_name) + 1\n\n"
            "        item = {\n"
            '            "id": task_id,\n'
            '            "path": path,\n'
            '            "queue_size": queue_size,\n'
            '            "metadata": {\n'
            '                "time_start": __import__("datetime").datetime.now().isoformat(),\n'
            '                "status": "pending",\n'
            '                "detail": "N/A",\n'
            '                "time_processing_start": "N/A",\n'
            '                "time_processing_end": "N/A",\n'
            '                "ip_address": __import__("socket").gethostbyname(__import__("socket").gethostname()),\n'
            "            },\n"
            "        }\n\n"
            '        self.hash_manager.create_hash(f"dvc:ticket:{task_id}", "metadata", item)\n'
            '        self.queue_manager.publish(self.queue_name, item)\n'
            '        self.sorted_set_manager.add_to_sorted_set(self.set_name, 0, task_id)\n'
            "        return item\n\n"
            "    def process_task(self, path: str, metadata: Dict[str, Any]) -> bool:\n"
            '        """Execute DVC pipeline: clean, add, push, inventory.\n'
            '        Override this method with your processing logic."""\n'
            "        import subprocess\n"
            "        from pathlib import Path\n\n"
            "        path_obj = Path(path)\n"
            "        if not path_obj.exists():\n"
            "            return False\n\n"
            "        # Step 1: Clean DVC temp\n"
            "        subprocess.run(\n"
            '            "rm -rf /app/.dvc/tmp && rm -rf /app/.dvc/cache",\n'
            "            shell=True, check=False\n"
            "        )\n\n"
            "        # Step 2: DVC add\n"
            "        subprocess.run(f\"dvc add {path}\", shell=True, check=True)\n\n"
            "        # Step 3: DVC push\n"
            "        push_path = f\"{path}.dvc\"\n"
            "        subprocess.run(f\"dvc push {push_path} -v\", shell=True, check=True)\n\n"
            "        # Step 4: Git remove tracking & commit\n"
            "        subprocess.run(f\"git rm -r --cached {path}\", shell=True, check=False)\n"
            '        subprocess.run(f\'git commit -m "stop tracking {path}"\', shell=True, check=False)\n\n'
            '        subprocess.run(\n'
            '            f"python /app/src/scripts/upload/files_inventory.py {path}",\n'
            '            shell=True, check=False)\n\n'
            "        return True\n\n"
            "    def start_worker(self):\n"
            '        """Start consuming tasks from queue."""\n'
            "        @self.queue_manager.on_message(self.queue_name)\n"
            "        def worker(message):\n"
            "            task_id = message.get(\"id\")\n"
            "            # Update status to processing\n"
            '            metadata = self.hash_manager.read_hash(f"dvc:ticket:{task_id}", "metadata")\n'
            '            metadata["metadata"]["status"] = "processing"\n'
            '            self.hash_manager.create_hash(f"dvc:ticket:{task_id}", "metadata", metadata)\n'
            '            self.sorted_set_manager.add_to_sorted_set(self.set_name, 1, task_id)\n'
            "            # Process\n"
            "            results = self.process_task(message[\"path\"], metadata)\n"
            "            # Update final status\n"
            '            self.sorted_set_manager.add_to_sorted_set(self.set_name, 2 if results else 3, task_id)\n'
            "            return results\n\n"
            "        self.queue_manager.start()\n"
            "        self.queue_manager.wait()\n"
        )

        # API template
        api_template = (
            "import gradio as gr\n"
            "from worker import DVCQueueWorker\n"
            "from config.settings import RedisSettings\n\n\n"
            "settings = RedisSettings.from_env()\n"
            "worker = DVCQueueWorker(settings)\n\n\n"
            "def add_to_queue(path: str):\n"
            '    """Submit file to DVC processing queue."""\n'
            "    return worker.submit_task(path)\n\n\n"
            "def get_status(task_id: str):\n"
            '    """Check task status by ID."""\n'
            '    from wredis.hash import RedisHashManager\n'
            '    hash_mgr = RedisHashManager(host=settings.host, port=settings.port, db=settings.db)\n'
            '    return hash_mgr.read_hash(f"dvc:ticket:{task_id}", "metadata")\n'
        )

        # Docker run script
        docker_run_template = (
            "#!/bin/bash\n"
            "# wDVC Worker Docker Run Script\n"
            "# This script starts the worker container for DVC data processing.\n\n"
            "set -euo pipefail\n\n"
            "# Configuration\n"
            'IMAGE="wisrovi/dataset-ia:worker-v1"\n'
            'IP_HOST="${IP_HOST:-192.168.1.84}"\n'
            'REDIS_HOST="${REDIS_HOST:-192.168.10.108}"\n'
            'PROJECTS_PATH="${PROJECTS_PATH:-$(pwd)/projects}"\n'
            'CPUS="${CPUS:-4.0}"\n'
            'MEMORY="${MEMORY:-4g}"\n'
            'SHM_SIZE="${SHM_SIZE:-16g}"\n\n'
            "mkdir -p \"${PROJECTS_PATH}\"\n\n"
            "echo \"Starting wDVC worker...\"\n"
            "echo \"  Image: ${IMAGE}\"\n"
            "echo \"  IP_HOST: ${IP_HOST}\"\n"
            "echo \"  REDIS_HOST: ${REDIS_HOST}\"\n"
            "echo \"  Projects: ${PROJECTS_PATH}\"\n"
            "echo \"  CPUs: ${CPUS}\"\n"
            "echo \"  Memory: ${MEMORY}\"\n"
            "echo \"  SHM: ${SHM_SIZE}\"\n\n"
            "docker run -it --rm \\\n"
            "  --name wdvc-worker \\\n"
            "  --hostname wDVC \\\n"
            "  --shm-size=\"${SHM_SIZE}\" \\\n"
            "  --cpus=\"${CPUS}\" \\\n"
            "  --memory=\"${MEMORY}\" \\\n"
            "  -e IP_HOST=\"${IP_HOST}\" \\\n"
            "  -e REDIS_HOST=\"${REDIS_HOST}\" \\\n"
            "  -v \"${PROJECTS_PATH}:/app/projects\" \\\n"
            "  -w /app \\\n"
            "  \"${IMAGE}\" \\\n"
            "  zsh\n"
        )

        # dvc.yaml template
        dvc_yaml_template = (
            "# wDVC Pipeline - Data Versioning Stages\n"
            "# Place this file at: dvc.yaml\n\n"
            "stages:\n"
            "  download:\n"
            "    cmd: python scripts/download/download_some_file.py ${FILE_PATH} --remote s3_remote\n"
            "    deps:\n"
            "      - .dvc/config\n"
            "    outs:\n"
            "      - data/raw/${FILE_PATH}:\n"
            "          cache: true\n"
            "          desc: \"Raw downloaded data from S3\"\n\n"
            "  process:\n"
            "    cmd: python scripts/process/process_data.py data/raw/${FILE_PATH} data/processed/\n"
            "    deps:\n"
            "      - data/raw/${FILE_PATH}\n"
            "    outs:\n"
            "      - data/processed/:\n"
            "          cache: true\n"
            "          desc: \"Processed dataset ready for training\"\n\n"
            "  push:\n"
            "    cmd: dvc push data/processed/\n"
            "    deps:\n"
            "      - data/processed/\n"
            "    desc: \"Push processed data to DVC remote\"\n\n"
            "  inventory:\n"
            "    cmd: python scripts/upload/files_inventory.py data/processed/\n"
            "    deps:\n"
            "      - data/processed/\n"
            "    outs:\n"
            "      - reports/inventory.csv:\n"
            "          cache: true\n"
            "          desc: \"File inventory CSV\"\n"
        )

        # Dockerfile.worker template
        dockerfile_worker_template = (
            "# wDVC Worker Dockerfile\n"
            "# Build: docker build -f Dockerfile.worker -t wisrovi/dataset-ia:worker-v1 .\n"
            "# This image runs the DVC worker that executes: dvc add, dvc push, git rm, dvc inventory\n\n"
            "FROM wisrovi/agents:gpu-slim-dvc\n"
            "SHELL [\"bash\", \"-c\"]\n\n"
            "WORKDIR /app\n\n"
            "# Git safe directory\n"
            "RUN git config --global --add safe.directory /app && \\\n"
            "    git config --system --add safe.directory /app\n\n"
            "# Copy DVC configuration\n"
            "COPY .dvc/ /app/.dvc/\n"
            "COPY dvc.lock /app/dvc.lock\n"
            "COPY dvc.yaml /app/dvc.yaml\n\n"
            "# Initialize git repo\n"
            "RUN git init && \\\n"
            "    git remote add origin https://github.com/wisrovi/dataset-IA.git && \\\n"
            "    git config --global user.email \"wrodriguez@ecapturedtech.com\" && \\\n"
            "    git config --global user.name \"wrodriguez\" && \\\n"
            "    git checkout -b DEVELOPMENT && \\\n"
            "    git add . && \\\n"
            "    git commit -m \"Initialize DVC pipeline\"\n\n"
            "# Install system deps\n"
            "RUN apt update && apt install -y nload && rm -rf /var/lib/apt/lists/*\n\n"
            "# Install Python deps\n"
            "COPY requirements.txt /app/requirements.txt\n"
            "RUN python -m pip install --no-cache-dir -r /app/requirements.txt\n\n"
            "# Health check\n"
            "HEALTHCHECK --interval=5m --timeout=30s --start-period=2m --retries=3 \\\n"
            "    CMD CURRENT_SIZE=$(du -sb / --exclude=/app/projects "
            "--exclude=/proc --exclude=/sys --exclude=/dev | cut -f1); \\\n"
            "    LIMIT=$((50 * 1024 * 1024 * 1024)); \\\n"
            "    if [ \"$CURRENT_SIZE\" -gt \"$LIMIT\" ]; then exit 1; else exit 0; fi\n\n"
            "# Copy source code\n"
            "COPY worker.py /app/worker.py\n"
            "COPY src/ /app/src/\n\n"
            "# Default command\n"
            "CMD [\"python\", \"/app/worker.py\"]\n"
        )

        # docker-compose.worker.yaml
        docker_compose_template = (
            "# wDVC Worker Docker Compose\n"
            "# Run: docker compose -f docker-compose.worker.yaml up worker\n\n"
            "services:\n\n"
            "  worker:\n"
            "    build:\n"
            "      context: .\n"
            "      dockerfile: Dockerfile.worker\n"
            "    image: wisrovi/dataset-ia:worker-v1\n"
            "    volumes:\n"
            "      - ./projects:/app/projects\n"
            "      # - ./.dvc/config:/app/.dvc/config\n"
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

        # Main entrypoint
        main_template = (
            "# wDVC Main Entrypoint\n"
            "# Run: python main.py\n\n"
            "from config.settings import RedisSettings\n"
            "from worker import DVCQueueWorker\n\n\n"
            "def run_worker():\n"
            '    """Start the wDVC queue worker."""\n'
            "    settings = RedisSettings.from_env()\n"
            "    worker = DVCQueueWorker(settings)\n\n"
            "    # Example: submit a task\n"
            '    # worker.submit_task("/app/projects/data/raw/my_dataset")\n\n'
            "    # Start consuming\n"
            "    worker.start_worker()\n\n\n"
            "if __name__ == \"__main__\":\n"
            "    run_worker()\n"
        )

        # Requirements
        requirements_template = (
            "wredis>=1.0.3\n"
            "redis>=5.0.0\n"
            "loguru>=0.7.0\n"
            "dvc>=3.59.0\n"
            "dvc-s3>=3.2.0\n"
            "boto3>=1.37.0\n"
            "pydantic>=2.0.0\n"
            "tqdm>=4.67.0\n"
            "rich>=14.0.0\n"
        )

        # README
        readme_template = (
            f"# {project_name.upper()}\n\n"
            "Professional DVC-backed data pipeline built with **wDVC**.\n\n"
            "## Architecture\n\n"
            "```mermaid\n"
            "flowchart TD\n"
            "    A[main.py] --> B[config/settings.py]\n"
            "    A --> C[worker/worker.py]\n"
            "    C --> D[(Redis: Queue + Hash + SortedSet)]\n"
            "    C --> E[DVC Pipeline]\n"
            "    E --> F[(DVC Remote: S3)]\n"
            "    C --> G[Docker Worker]\n"
            "    G --> H[projects/ volume]\n"
            "    style D fill:#ff6b6b,stroke:#333\n"
            "    style E fill:#4ecdc4,stroke:#333\n"
            "    style F fill:#ffe66d,stroke:#333\n"
            "```\n\n"
            "## Quick Start\n\n"
            "### 1. Start the Worker (for data download/processing)\n"
            "```bash\n"
            "./run_worker.sh\n"
            "# OR manually:\n"
            "mkdir -p projects\n"
            "docker run -it --rm \\\n"
            "  --name wdvc-worker \\\n"
            "  --hostname wDVC \\\n"
            "  --shm-size=16g \\\n"
            "  --cpus=4.0 \\\n"
            "  --memory=4g \\\n"
            "  -e IP_HOST=192.168.1.84 \\\n"
            "  -e REDIS_HOST=192.168.10.108 \\\n"
            "  -v $(pwd)/projects:/app/projects \\\n"
            "  -w /app \\\n"
            "  wisrovi/dataset-ia:worker-v1 \\\n"
            "  zsh\n"
            "# Inside container:\n"
            "python worker.py\n"
            "```\n\n"
            "### 2. Or use Docker Compose\n"
            "```bash\n"
            "docker compose -f docker-compose.worker.yaml up worker\n"
            "```\n\n"
            "### 3. Submit tasks via Python\n"
            "```python\n"
            "from worker import DVCQueueWorker\n"
            "from config.settings import RedisSettings\n\n"
            "settings = RedisSettings.from_env()\n"
            "worker = DVCQueueWorker(settings)\n"
            "worker.submit_task(\"/app/projects/data/raw/my_dataset\")\n"
            "worker.start_worker()\n"
            "```\n\n"
            "### 4. Web UI (Gradio)\n"
            "```bash\n"
            "python api.py\n"
            "# Open http://localhost:7860\n"
            "```\n\n"
            "## Project Structure\n\n"
            "```\n"
            f"{project_name}/\n"
            "├── config/\n"
            "│   ├── __init__.py\n"
            "│   └── settings.py          # RedisSettings from environment\n"
            "├── worker/\n"
            "│   ├── __init__.py\n"
            "│   └── worker.py            # DVCQueueWorker\n"
            "├── api/\n"
            "│   ├── __init__.py\n"
            "│   └── api.py               # Gradio web UI\n"
            "├── scripts/\n"
            "│   ├── download/\n"
            "│   ├── process/\n"
            "│   └── upload/\n"
            "├── tests/\n"
            "├── projects/                # Mounted volume (gitignored)\n"
            "├── .dvc/\n"
            "│   └── config               # DVC remote config\n"
            "├── dvc.yaml                 # Pipeline stages\n"
            "├── dvc.lock\n"
            "├── requirements.txt\n"
            "├── Dockerfile.worker\n"
            "├── docker-compose.worker.yaml\n"
            "├── run_worker.sh            # Docker run script\n"
            "├── main.py                  # Service entrypoint\n"
            "��── README.md\n"
            "```\n\n"
            "## Running Tests\n\n"
            "```bash\n"
            "pytest tests/ -v\n"
            "pytest tests/ --cov=src --cov-report=html\n"
            "```\n\n"
            "## Docker\n\n"
            "```bash\n"
            "docker build -f Dockerfile.worker -t wisrovi/dataset-ia:worker-v1 .\n"
            "./run_worker.sh\n"
            "```\n\n"
            "---\n"
            "*Generated by wDVC MCP by **wisrovi***\n"
        )

# Base blueprints for each scaffold type
        if scaffold_type == "worker_service":
            blueprints = {
                "requirements.txt": requirements_template,
                "README.md": readme_template,
                "config/__init__.py": "from .settings import RedisSettings\n",
                "config/settings.py": settings_template,
                "worker/__init__.py": "from .worker import DVCQueueWorker\n",
                "worker/worker.py": worker_template,
                "scripts/__init__.py": "",
                "dvc.yaml": dvc_yaml_template,
                "Dockerfile.worker": dockerfile_worker_template,
                "docker-compose.worker.yaml": docker_compose_template,
                "run_worker.sh": docker_run_template,
                "main.py": main_template,
                ".wdvc/config.json": '{\n  "enableBackupFile": true,\n  "maxSearchFiles": 500\n}\n',
            }
        elif scaffold_type == "api_service":
            blueprints = {
                "requirements.txt": requirements_template,
                "README.md": readme_template,
                "config/__init__.py": "from .settings import RedisSettings\n",
                "config/settings.py": settings_template,
                "api/__init__.py": "from .api import add_to_queue, get_status\n",
                "api/api.py": api_template,
                "scripts/__init__.py": "",
                "dvc.yaml": dvc_yaml_template,
                "Dockerfile.worker": dockerfile_worker_template,
                "docker-compose.worker.yaml": docker_compose_template,
                "run_worker.sh": docker_run_template,
                "main.py": main_template,
                ".wdvc/config.json": '{\n  "enableBackupFile": true,\n  "maxSearchFiles": 500\n}\n',
            }
        elif scaffold_type == "full_pipeline":
            blueprints = {
                "requirements.txt": requirements_template,
                "README.md": readme_template,
                "config/__init__.py": "from .settings import RedisSettings\n",
                "config/settings.py": settings_template,
                "worker/__init__.py": "from .worker import DVCQueueWorker\n",
                "worker/worker.py": worker_template,
                "api/__init__.py": "from .api import add_to_queue, get_status\n",
                "api/api.py": api_template,
                "scripts/__init__.py": "",
                "scripts/download/download_some_file.py": (
                    "# DVC File Downloader\n"
                    "from src.scripts.download.download_some_file import DVCFileDownloader\n"
                ),
                "scripts/process/process_data.py": (
                    "# Data Processing Script\n"
                    "def process(input_path: str, output_path: str):\n"
                    "    pass\n"
                ),
                "scripts/upload/files_inventory.py": (
                    "# File Inventory Generator\n"
                    "def generate_inventory(data_path: str):\n"
                    "    pass\n"
                ),
                "dvc.yaml": dvc_yaml_template,
                "Dockerfile.worker": dockerfile_worker_template,
                "docker-compose.worker.yaml": docker_compose_template,
                "run_worker.sh": docker_run_template,
                "main.py": main_template,
                ".wdvc/config.json": '{\n  "enableBackupFile": true,\n  "maxSearchFiles": 500\n}\n',
            }
        else:  # standard
            blueprints = {
                "requirements.txt": requirements_template,
                "README.md": readme_template,
                "config/__init__.py": "from .settings import RedisSettings\n",
                "config/settings.py": settings_template,
                "worker/__init__.py": "from .worker import DVCQueueWorker\n",
                "worker/worker.py": worker_template,
                "api/__init__.py": "from .api import add_to_queue, get_status\n",
                "api/api.py": api_template,
                "scripts/__init__.py": "",
                "dvc.yaml": dvc_yaml_template,
                "Dockerfile.worker": dockerfile_worker_template,
                "docker-compose.worker.yaml": docker_compose_template,
                "run_worker.sh": docker_run_template,
                "main.py": main_template,
                ".wdvc/config.json": '{\n  "enableBackupFile": true,\n  "maxSearchFiles": 500\n}\n',
            }

        return blueprints
