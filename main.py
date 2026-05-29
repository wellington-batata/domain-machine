import sys, os
import utils.files as file_utils
import utils.date_and_time as date_utils
import aws_files as aws_utils
import process_batch as executor_batch

from dotenv import load_dotenv
load_dotenv()

def main():
    bucket_name = os.getenv("AWS_S3_BUCKET_NAME")

    if len(sys.argv) == 2:
      param_string = sys.argv[1]
      print(f"Iniciar a partir do arquivo: {param_string}")
      re_process(bucket_name, param_string)
    else:
      print("Nenhum arquivo especificado. Use: python main.py <nome do arquivo no bucket>")
      sys.exit(1)

def re_process(bucket_name, file_key):
    domains_folder = os.getenv("DOMAINS_FOLDER", "registrobr")
    download_dir = os.getenv("DOWNLOAD_S3_DIR", "files/download")
    
    files_list = aws_utils.list_files_s3(bucket_name, prefix=f"{domains_folder}/{file_key}")

    if len(files_list) > 0:
      registrobr_file = files_list[0]
      print(f"{len(files_list)} Arquivo encontrado: {registrobr_file}")

      domains_file = aws_utils.download_file_from_s3(bucket_name, registrobr_file, f"{download_dir}/{file_key}")
      lines = file_utils.read_lines_slice(domains_file, start_line=0, num_lines=1)
      date_of_file = date_utils.extract_date_registrobr(lines[0])
      ## TODO: MUDAR FUNÇÃO DEPOIS DOS TESTES
      domains_list = file_utils.read_lines_slice(domains_file, start_line=10000, num_lines=350)
      print(f"Data extraída do arquivo: {date_of_file} | Total de domínios: {len(domains_list)}")
      executor_batch.process_batch(domains_list, bucket_name, date_of_file)

if __name__ == "__main__":
    main()