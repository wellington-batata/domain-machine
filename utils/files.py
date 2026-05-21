from pathlib import Path
import json
from typing import Any
from datetime import datetime

def read_lines(path: str, skip_comments: bool = True) -> list[str]:
    p = Path(path)
    if not p.is_file():
        return []
    lines = p.read_text(encoding="utf-8").splitlines()
    if skip_comments:
        lines = [line.strip() for line in lines if line.strip() and not line.strip().startswith("#")]
    return lines


def read_json(path: str, default: Any = None) -> Any:
    p = Path(path)
    if not p.is_file():
        return default
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path: str, data: Any, indent: int = 4) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)


def append_jsonl(path: str, data: Any) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")


def write_jsonl(path: str, content: Any) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)

    if hasattr(content, "read"):
        raw_content = content.read()
    elif hasattr(content, "text"):
        raw_content = content.text
    else:
        raw_content = content

    if isinstance(raw_content, bytes):
        text = raw_content.decode("utf-8", errors="replace")
    else:
        text = str(raw_content)

    with p.open("w", encoding="utf-8") as f:
        f.write(text)

def generate_filename(prefix: str, extension: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d%H%M")
    return f"{prefix}_{timestamp}.{extension}"



