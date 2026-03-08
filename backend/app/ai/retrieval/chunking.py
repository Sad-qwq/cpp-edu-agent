def estimate_token_count(text: str) -> int:
    return max(1, len(text) // 4) if text else 0


def split_text(text: str, *, chunk_size: int = 800, overlap: int = 100) -> list[str]:
    content = (text or "").strip()
    if not content:
        return []

    if len(content) <= chunk_size:
        return [content]

    chunks: list[str] = []
    start = 0
    while start < len(content):
        end = min(len(content), start + chunk_size)
        chunks.append(content[start:end].strip())
        if end >= len(content):
            break
        start = max(0, end - overlap)
    return [chunk for chunk in chunks if chunk]