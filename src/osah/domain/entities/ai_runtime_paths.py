from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class AiRuntimePaths:
    """Шляхи до локального AI-runtime ClearWork.
    Paths to the local ClearWork AI runtime bundle.
    """

    server_executable: Path
    primary_model_path: Path
    fallback_model_path: Path | None
    server_log_path: Path
    server_host: str = "127.0.0.1"
    server_port: int = 18765
