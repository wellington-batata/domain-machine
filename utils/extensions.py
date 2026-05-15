import os

from schemas import Extensions, ExtensionItem, Domain
import utils.files as file_utils

def extract_extensions(extensions: list[ExtensionItem], preference_ext: list[str]):
    preferred = []
    ignored = []
    for item in extensions:
        ext = item["ext"]
        count = item["count"]
        if ext in preference_ext:
            preferred.append({"ext": ext, "count": count})
        else:
            ignored.append({"ext": ext, "count": count})
    return preferred, ignored


def filter_by_extensions(domains: list[Domain], allowed_exts: list[str]) -> list[Domain]:
    return [d for d in domains if get_extension(d.domain) in allowed_exts]

def get_extension(domain: str) -> str:
    parts = domain.strip().lstrip(".").split(".")
    # Domínio direto: nome.br
    if len(parts) == 2:
        return "." + parts[-1]
    
    # Padrão normal: nome.categoria.br → pega categoria.br
    return "." + ".".join(parts[-2:])


def extension_organize(extensions: dict[str, int], preference_ext: list[str], ext_type_file: str) -> Extensions:
    if os.path.exists(ext_type_file):
        data = file_utils.read_json(ext_type_file, default={"extensions": [], "ignored": []})
        return Extensions(**data)
    else:
        preferred, ignored = extract_extensions(extensions, preference_ext)
        file_utils.write_json(ext_type_file, {"extensions": preferred, "ignored": ignored}, indent=2)
        return Extensions(extensions=preferred, ignored=ignored)
    

def count_by_extension(domains: list[str]) -> dict[str, int]:
    ext_counts = {}
    for domain in domains:
        ext = get_extension(domain)
        if ext:
            ext_counts[ext] = ext_counts.get(ext, 0) + 1
    
    return [{"ext": k, "count": v} for k, v in ext_counts.items()]