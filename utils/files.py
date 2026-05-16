from pathlib import Path
import json
from typing import Any


def read_lines(path: str, skip_comments: bool = True) -> list[str]:
    p = Path(path)
    if not p.is_file():
        return []
    lines = p.read_text(encoding="utf-8").splitlines()
    if skip_comments:
        lines = [line.strip() for line in lines if line.strip() and not line.strip().startswith("#")]
    return lines[1:100]


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