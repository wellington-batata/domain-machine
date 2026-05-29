from dotenv import load_dotenv
load_dotenv()

from utils.domains import split_into_batches, domains_to_jsonl , build_domains

import utils.files as file_utils
import utils.extensions as ext_utils
import aws_files as aws_utils

import os

def process_batch(domains_list: list[str], bucket_name: str, file_key: str):
    # Lógica para processar os domínios em batch
    # 1. Ler os arquivos de domínios do S3
    # 2. Aplicar os filtros (números, caracteres especiais, tamanho)
    # 3. Gerar os arquivos de saída para upload


  chunk_size = int(os.getenv("CHUNK_SIZE", 150))
  dir_batches = f"{os.getenv("DIR_BATCHES", "batches")}/{file_key}"
  preferences_file = aws_utils.download_file_from_s3(bucket_name, f"preferences.json", dir_batches)
  preference_ext = file_utils.read_json(preferences_file, default=[])
  # domains_ext = ext_utils.count_by_extension(domains_list)
  # selected_ext = [item.ext for item in domains_ext.ext if item.ext in preference_ext]
  domains_clean = build_domains(domains_list, preference_ext)

  batches = split_into_batches(domains_clean, batch_size=chunk_size)
  for ibatch, batch in enumerate(batches):
      name_output_json = f"{file_utils.generate_filename(f'batch_{ibatch+1}', 'jsonl')}"
      list_obj = domains_to_jsonl(batch)
      aws_utils.create_file_s3(bucket_name, f"{dir_batches}/{name_output_json}", list_obj, "application/x-ndjson")
      print(f"Batch {ibatch+1} criado e salvo em S3: {dir_batches}/{name_output_json}")

  print(f"{len(batches)} Arquivos preparados em: {dir_batches}\n")