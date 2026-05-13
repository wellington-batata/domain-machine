from schemas import Extensions, ExtensionItem, Domain

def extract_extensions(extensions: list[ExtensionItem], preference_ext: list[str]) -> Extensions:
    preferred = []
    ignored = []
    for item in extensions:
        ext = item["ext"]
        count = item["count"]
        if ext in preference_ext:
            preferred.append(ExtensionItem(ext=ext, count=count))
        else:
            ignored.append(ExtensionItem(ext=ext, count=count))
    return Extensions(extensions=preferred, ignored=ignored)


def filter_by_extensions(domains: list[str], allowed_exts: list[str]) -> list[Domain]:
    return [Domain(domain=domain) for domain in domains if get_extension(domain) in allowed_exts]

def get_extension(domain: str) -> str:
    if "." in domain:
        return domain[domain.index("."):]
    return ""