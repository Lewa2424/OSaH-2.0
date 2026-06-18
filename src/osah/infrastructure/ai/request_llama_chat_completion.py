import json
import urllib.error
import urllib.request


class LlamaServerHttpError(RuntimeError):
    """Помилка HTTP від llama-server з тілом відповіді.
    HTTP error from llama-server including response body.
    """

    def __init__(
        self,
        message: str,
        *,
        status_code: int,
        response_body: str,
        request_bytes: int,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body
        self.request_bytes = request_bytes


def request_llama_chat_completion(
    base_url: str,
    *,
    system_prompt: str,
    user_prompt: str,
    max_tokens: int = 256,
    temperature: float = 0.1,
    timeout_seconds: float = 120.0,
) -> str:
    """Надсилає chat-completion запит до llama-server.
    Sends a chat completion request to llama-server.
    """

    request_body = json.dumps(
        {
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        },
        ensure_ascii=False,
    ).encode("utf-8")
    request = urllib.request.Request(
        f"{base_url.rstrip('/')}/v1/chat/completions",
        data=request_body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        body = error.read().decode("utf-8", errors="replace")
        raise LlamaServerHttpError(
            f"llama-server HTTP {error.code}: {body[:500]}",
            status_code=error.code,
            response_body=body,
            request_bytes=len(request_body),
        ) from error
    except urllib.error.URLError as error:
        raise RuntimeError(f"llama-server недоступний: {error}") from error

    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices:
        raise RuntimeError("llama-server повернув порожню відповідь.")

    message = choices[0].get("message", {})
    content = message.get("content")
    if not isinstance(content, str) or not content.strip():
        raise RuntimeError("llama-server не повернув текст відповіді.")

    return content.strip()
