import json
import uuid
import utils.files as file_utils
import utils.domains as domain_utils
import prompt_template as prompt_template

def to_upload(domains: list[str], output_dir: str):
    """
    Prepara os domínios para upload em batch.
    Args:        
        domains: Lista de domínios a serem processados.
        output_dir: Diretório onde os arquivos organizados por extensão serão salvos.
    output:
        Cria arquivos organizados por extensão e um arquivo batch_dominios.jsonl para upload
    """
    linhas = []
    for domain in domains:
        domain_name = domain_utils.get_domain_name(domain);
        linha = {
            "custom_id": f"domain-{uuid.uuid4().hex[:8]}",  # ID único para mapear depois
            "method": "POST",
            "url": "/v1/chat/completions",
            "body": {
                "model": "gpt-4o-mini",
                "max_tokens": 200,
                "messages": [
                    {
                        "role": "system",
                        "content": f"{prompt_template.get_system_prompt_domains()}"
                    },
                    {
                        "role": "user",
                        "content": f"{prompt_template.get_user_prompt_domain(domain, len(domain_name))}"
                    }
                ]
            }
        }
        linhas.append(linha)
    
    file_utils.write_json(f"{output_dir}", linhas, indent=None)