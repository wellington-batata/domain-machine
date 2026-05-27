import os
import time

from openai import OpenAI
from typing import List
from openai import OpenAI
from schemas import OpenAI_Batch
from utils import files as file_utils, date_and_time as date_utils

def create_client() -> OpenAI:
    api_key = os.getenv("OPENAI_API_KEY") or os.getenv("API_KEY")
    if not api_key:
        raise ValueError("Defina OPENAI_API_KEY (ou API_KEY) no ambiente.")
    return OpenAI(api_key=api_key)

def send_one_batch(client: OpenAI, file_path: str):
    with open(file_path, "rb") as f:
        file = client.files.create(file=f, purpose="batch")
        batch = client.batches.create(
            input_file_id=file.id,
            endpoint="/v1/chat/completions",
            completion_window="24h",
            metadata={"descricao": f"Processamento de dominios do arquivo {file_path}"}
        )

        batch_obj = OpenAI_Batch(
          batch_id=batch.id,
          file_id=file.id,
          input_file_id=file.id
        ) 

    print(f"Arquivo: {file_path} | file_id: {file.id} | batch_id: {batch.id} | status: {batch.status}")
    return batch_obj

def to_check_status_batch_openai(batch_ids: List[str]):
    """
    Verifica o status dos batches na OpenAI.
    Args:
        batch_ids: Lista de IDs dos batches a serem verificados.
    Output:
        Imprime o status de cada batch.
    """
    client = create_client()

    for batch_id in batch_ids:
        batch = client.batches.retrieve(batch_id)
        print(f"Batch ID: {batch.id} | Status: {batch.status} | Completos: {batch.request_counts.completed}/{batch.request_counts.total}")
        if batch.status == "completed":
            content = client.files.content(batch.output_file_id)
            print(f" >>>>> Processamento do batch {batch.id} completo. Baixando resultados...")
            file_utils.write_jsonl(f"files/outputs/{batch.id}.jsonl", content)
            print(f" >>>>> Resultados do batch {batch.id} salvos em files/outputs/{batch.id}.jsonl")
    print(f"\n\n")

def to_send_batch_openai(file_paths: List[str]):
    """
    Prepara o arquivo JSONL para envio em batch na OpenAI.
    Args:
        file_paths: Lista de caminhos dos arquivos JSONL a serem preparados.
    Output:
        Retorna uma lista de dicionários prontos para envio em batch.
    """
    client = create_client()
    batch_outputs = []
    for path in file_paths:
      batch_obj = send_one_batch(client, path)  
      batch_outputs.append(batch_obj)

    print(f"=============== SALVAR ================")
    for batch_output in batch_outputs:
        print(f"Batch ID: {batch_output.batch_id} | File ID: {batch_output.file_id} | Input File ID: {batch_output.input_file_id}")
    print(f"=======================================")

def get_batch_status(client: OpenAI, batch_id: str): 
    batch = client.batches.retrieve(batch_id)
    print(f"{date_utils.log_now()} | Batch ID: {batch.id} | Status: {batch.status} | Completos: {batch.request_counts.completed}/{batch.request_counts.total}")
    return batch

def download_batch_output(client: OpenAI, file_id: str, output_path: str):
    content = client.files.content(file_id)
    file_utils.write_jsonl(output_path, content)
    print(f"Download salvo em {output_path}\n")

def to_step_by_step_processing(file_paths: List[str], interval_check: int = 30):
    """
    Processa os arquivos JSONL um a um, enviando requisições sequenciais para a OpenAI.
    Args:
        file_paths: Lista de caminhos dos arquivos JSONL a serem processados.
        interval_check: Intervalo em segundos para verificar o status dos batches.
    Output:
        Imprime os resultados de cada arquivo à medida que são processados.
    """
    client = create_client()
    dir_output = os.getenv("DIR_OUTPUT", "files/batches")
    to_process = file_utils.generate_filename("to_process", "jsonl")
    file_utils.write_json(f"{dir_output}/{to_process}", file_paths)
    error_list = []
    try:
        for path in file_paths:
            print(f"Processando arquivo: {path}")
            batch_obj = send_one_batch(client, path)

            while True:
                
                batch = get_batch_status(client, batch_obj.batch_id)

                if batch.status == "completed":
                    output_path = f"{dir_output}/output_{os.path.basename(path)}"
                    download_batch_output(client, batch.output_file_id, output_path)
                    break
                
                # elif batch.status in ["cancelling"]:
                #     print(f"Batch {batch.id} em cancelamento. Aguardando cancelamento total ...")
                #     time.sleep(interval_check)
                #     continue
                
                elif batch.status in ["failed", "cancelled", "expired"]:
                    print(f"Batch {batch.id} com status {batch.status}. Verifique os detalhes na OpenAI Dashboard.")
                    if batch.id not in error_list:
                        error_list.append(batch.id)
                        file_utils.append_jsonl(f"{dir_output}/failed_batches.jsonl", {"batch_id": batch.id, "status": batch.status, "file_path": path})
                    break
                time.sleep(interval_check)  # Espera o intervalo definido antes de verificar novamente

    except Exception as e:
        print(f"Erro ao processar arquivos: {e}")
        client.close()  # Fecha o cliente para liberar recursos
        return
    finally:
        print("Processamento step-by-step concluído.\n")

