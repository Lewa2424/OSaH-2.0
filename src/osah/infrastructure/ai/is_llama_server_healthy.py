import json
import urllib.error
import urllib.request


def is_llama_server_healthy(base_url: str, *, timeout_seconds: float = 2.0) -> bool:
    """Перевіряє готовність llama-server через /health.
    Checks llama-server readiness through /health.
    """

    request = urllib.request.Request(f"{base_url.rstrip('/')}/health", method="GET")
    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, ValueError):
        return False

    return payload.get("status") == "ok"
