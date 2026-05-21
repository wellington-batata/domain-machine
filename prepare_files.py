# import uuid
from typing import List
from openai import OpenAI
import os

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
    for domain in domains:
        domain_name = domain_utils.get_domain_name(domain);
        jsonline = {
            #"custom_id": f"domain-{uuid.uuid4().hex[:8]}",  # ID único para mapear depois
            "custom_id": domain,
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
        file_utils.append_jsonl(f"{output_dir}", jsonline)


def to_send_batch_openai(file_paths: List[str]):
    """
    Prepara o arquivo JSONL para envio em batch na OpenAI.
    Args:
        file_paths: Lista de caminhos dos arquivos JSONL a serem preparados.
    Output:
        Retorna uma lista de dicionários prontos para envio em batch.
    """
    client = OpenAI(api_key=os.getenv("API_KEY"))
    batch_ids = []
    for path in file_paths:
        with open(path, "rb") as f:
            file = client.files.create(file=f, purpose="batch")
            print(f"Enviando arquivo {path}. file_id: {file.id}")

            batch = client.batches.create(
                input_file_id=file.id,
                endpoint="/v1/chat/completions",
                completion_window="24h",
                metadata={"descricao": f"Processamento de domínios do arquivo {path}"}
            )
            print(f"Batch criado para {path}. batch_id: {batch.id} | status: {batch.status}")
            batch_ids.append(batch.id)
    
        print(f"=============== SALVAR ================")
    for batch_id in batch_ids:
        print(f"Batch ID: {batch_id}")
    print(f"=======================================")


def to_check_status_batch_openai(batch_ids: List[str]):
    """
    Verifica o status dos batches na OpenAI.
    Args:
        batch_ids: Lista de IDs dos batches a serem verificados.
    Output:
        Imprime o status de cada batch.
    """
    client = OpenAI(api_key=os.getenv("API_KEY"))

    for batch_id in batch_ids:
        batch = client.batches.retrieve(batch_id)
        print(f"Batch ID: {batch.id} | Status: {batch.status} | Completos: {batch.request_counts.completed}/{batch.request_counts.total}")
        if batch.status == "completed":
            content = client.files.content(batch.output_file_id)
            print(f" >>>>> Processamento do batch {batch.id} completo. Baixando resultados...")
            file_utils.write_jsonl(f"files/outputs/{batch.id}.jsonl", content)
            print(f" >>>>> Resultados do batch {batch.id} salvos em files/outputs/{batch.id}.jsonl")
    print(f"\n\n")

