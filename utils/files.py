import json
import prompt_template

from pathlib import Path
from typing import Any
from datetime import datetime
import utils.files as file_utils
import utils.domains as domain_utils
from schemas import Domain

def read_lines(path: str, skip_comments: bool = True) -> list[str]:
    p = Path(path)
    if not p.is_file():
        return []
    lines = p.read_text(encoding="utf-8").splitlines()
    if skip_comments:
        lines = [line.strip() for line in lines if line.strip() and not line.strip().startswith("#")]
    return lines[10000:10100]


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

def to_upload(domains: list[Domain], output_dir: str):
    """
    Prepara os domínios para upload em batch.
    Args:        
        domains: Lista de domínios a serem processados.
        output_dir: Diretório onde os arquivos organizados por extensão serão salvos.
    output:
        Cria arquivos organizados por extensão e um arquivo batch_dominios.jsonl para upload
    """
    for d in domains:
        domain_name = domain_utils.get_domain_name(d.domain);
        jsonline = {
            #"custom_id": f"domain-{uuid.uuid4().hex[:8]}",  # ID único para mapear depois
            "custom_id": d.domain,  # ID usando o próprio domínio para facilitar mapeamento
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "model": "gpt-4o-2024-11-20",
                "max_tokens": 200,
                "messages": [
                    {
                        "role": "system",
                        "content": f"{prompt_template.get_system_prompt_domains()}"
                    },
                    {
                        "role": "user",
                        "content": f"{prompt_template.get_user_prompt_domain(d.domain, len(domain_name))}"
                    }
                ]
            }
        }
        file_utils.append_jsonl(f"{output_dir}", jsonline)