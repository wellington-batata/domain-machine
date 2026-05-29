from ast import List
import json
from typing import List
import utils.prompt_template as prompt_template
from schemas import Domain, DomainDetail
import utils.extensions as ext_utils
import utils.domains as domain_utils

def get_domain_name(domain: str) -> str:
    parts = domain.strip().lstrip(".").split(".")
    if len(parts) > 0:
        return parts[0]
    return domain

def build_domains(domains_raw, preferred_extensions):
    result = []
    for raw in domains_raw:
        ext = ext_utils.get_extension(raw)
        name = get_domain_name(raw)

        matched_ext = ""
        for pe in preferred_extensions:
            if raw.endswith(pe):
                matched_ext = pe
                break

        base = raw[:-len(matched_ext)] if matched_ext else name
        has_numbers = any(ch.isdigit() for ch in name)
        has_special_chars = ("." in base) or ("-" in base)
        length = len(base)

        detail = DomainDetail(
            domain_name=name,
            extension=ext,
            length=length,
            has_numbers=has_numbers,
            has_special_chars=has_special_chars,
        )
        result.append(Domain(domain=raw, detail=detail))
    return result



def numbers_filter(domains: list[Domain]):
    """
    Separa domínios que contêm números dos que não contêm.
    
    Args:
        domains (list): Lista de domínios
        
    Returns:
        tuple: (domínios_com_números, domínios_sem_números)
    """
    filter_with_numbers = []
    filter_without_numbers = []
    
    for d in domains:
        if any(char.isdigit() for char in d.domain):
            filter_with_numbers.append(d)
        else:
            filter_without_numbers.append(d)
    
    return filter_with_numbers, filter_without_numbers


def special_chars_filter(domains: list[Domain], preferred_extensions: list[str]):
    """
    Separa domínios que contêm pontos (.) ou hifens (-) além das extensões preferenciais.
    
    Args:
        domains (list): Lista de domínios
        preferred_extensions (list): Lista de extensões preferenciais (ex: ['.com.br', '.adv.br'])
        
    Returns:
        tuple: (domínios_com_pontos_ou_hifens, domínios_limpos)
    """
    domains_with_special_chars = []
    domains_clean = []
    
    for d in domains:
        # Remove a extensão preferencial para verificar se há pontos ou hifens extras
        domain_without_ext = d.domain
        for ext in preferred_extensions:
            if d.domain.endswith(ext):
                domain_without_ext = d.domain[:-len(ext)]
                break
        
        # Verifica se há pontos ou hifens no domínio sem a extensão
        if '.' in domain_without_ext or '-' in domain_without_ext:
            domains_with_special_chars.append(d)
        else:
            domains_clean.append(d)
    
    return domains_with_special_chars, domains_clean


def size_filter(domains: list[Domain], preferred_extensions, char_limit):
    """
    Filtra domínios longos recebendo um limite de corte para separar os maiores.
    
    Args:
        domains (list): Lista de domínios
        preferred_extensions (list): Lista de extensões preferenciais (ex: ['.com.br', '.adv.br'])
        char_limit (int): Limite de caracteres para considerar um domínio como longo
        
    Returns:
        tuple: (domínios_longos_com_tamanho, domínios_curtos_com_tamanho)
            Cada elemento é uma lista de tuplas (domínio, tamanho_sem_extensão)
    """
    filter_long = []
    filter_short = []
    
    for d in domains:
        # Remove a extensão preferencial para contar caracteres
        domain_without_ext = d.domain
        for ext in preferred_extensions:
            if d.domain.endswith(ext):
                domain_without_ext = d.domain[:-len(ext)]
                break
        
        # Conta caracteres sem a extensão
        char_count = len(domain_without_ext)
        
        if char_count > char_limit:
            filter_long.append(d)
        else:
            filter_short.append(d)
    
    return filter_long, filter_short

def split_into_batches(domains: List[str], batch_size: int) -> List[List[str]]:
    """Divide dominios em batches"""
    return [domains[i:i + batch_size] for i in range(0, len(domains), batch_size)]


def domains_to_jsonl(domains: List[Domain]) -> str:
    lines = []

    for d in domains:
        domain_name = domain_utils.get_domain_name(d.domain)
        obj = {
            "custom_id": d.domain,
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "model": "gpt-4o-2024-11-20",
                "max_tokens": 200,
                "messages": [
                    {
                        "role": "system",
                        "content": prompt_template.get_system_prompt_domains()
                    },
                    {
                        "role": "user",
                        "content": prompt_template.get_user_prompt_domain(d.domain, len(domain_name))
                    }
                ]
            }
        }
        lines.append(json.dumps(obj, ensure_ascii=False))
    
    return "\n".join(lines) + "\n"
