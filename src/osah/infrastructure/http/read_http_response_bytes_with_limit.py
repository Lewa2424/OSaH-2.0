from osah.domain.services.http_fetch_limits import MAX_HTTP_RESPONSE_BYTES


# ###### ЧИТАННЯ HTTP-ВІДПОВІДІ З ЛІМІТОМ / READ HTTP RESPONSE WITH BYTE LIMIT ######
def read_http_response_bytes_with_limit(
    response,
    *,
    max_bytes: int = MAX_HTTP_RESPONSE_BYTES,
) -> bytes:
    """Читає тіло HTTP-відповіді з обмеженням розміру.
    Reads HTTP response body with a size cap.
    """

    chunks: list[bytes] = []
    total_size = 0
    while True:
        chunk = response.read(65536)
        if not chunk:
            break
        total_size += len(chunk)
        if total_size > max_bytes:
            raise ValueError(f"Відповідь перевищує ліміт {max_bytes} байт.")
        chunks.append(chunk)
    return b"".join(chunks)
