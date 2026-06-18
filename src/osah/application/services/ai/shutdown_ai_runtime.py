"""Зупиняє llama-server при завершенні застосунку.
Stops llama-server when the application shuts down.
"""

from osah.infrastructure.ai.llama_server_session import stop_llama_server_process


def shutdown_ai_runtime() -> None:
    """Завершує локальний AI-runtime.
    Shuts down the local AI runtime.
    """

    stop_llama_server_process()
