"""utils/helpers.py — small reusable utility functions used across modules."""

import hashlib
import re
from datetime import datetime
from pathlib import Path


def generate_doc_id(file_path: Path) -> str:
    """
    Deterministic ID for a document, based on filename + content hash.
    Re-uploading the identical file produces the same doc_id (so we can
    detect duplicates); a changed file produces a new one.
    """
    content_hash = hashlib.sha256(Path(file_path).read_bytes()).hexdigest()[:10]
    safe_name = re.sub(r"[^a-zA-Z0-9_]", "_", Path(file_path).stem)
    return f"{safe_name}_{content_hash}"


def timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def truncate_text(text: str, max_chars: int = 200) -> str:
    return text if len(text) <= max_chars else text[:max_chars].rstrip() + "..."
