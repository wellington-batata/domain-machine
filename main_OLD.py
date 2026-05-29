from dotenv import load_dotenv
import os
import sys

from utils.domains import build_domains, numbers_filter, size_filter, special_chars_filter, split_into_batches
import utils.files as file_utils
import utils.extensions as ext_utils
from openai_client import to_send_batch_openai, to_step_by_step_processing

load_dotenv()
    
if __name__ == "__main__":

    # Receber argumento e opção de await
    await_option = None
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        if arg in ['yes', 'y']:
            await_option = True
        elif arg in ['no', 'n']:
            await_option = False
        else:
            print("Argumento inválido. Use: yes/y ou no/n")
            sys.exit(1)
    else:
        response = input("Processar em step-by-step? (yes/no): ")
        await_option = response in ['yes', 'y', 'Yes', 'YES', 'Y']

    start_line = None
    if len(sys.argv) > 2:
        start_line = int(sys.argv[2])

    
    print(f"Step-by-step option: {await_option}\n")
    # exit(0)
    
    # Caminho do arquivo com os domínios
    domains_file = os.getenv("DOMAIN_LIST_FILE", "domains.txt")
    extensions_file = os.getenv("DOMAIN_EXTENSIONS", "domain_types.json")
    preference_file = os.getenv("DOMAIN_PREF_EXTENSIONS", "files/preference.json")
    dir_batches = os.getenv("DIR_BATCHES", "files/batches")
    dir_output = os.getenv("DIR_OUTPUT", "files/outputs")
    chunk_size = int(os.getenv("CHUNK_SIZE", 20000))
    size_domains = 16
    time_wait = int(os.getenv("STEP_BY_STEP_TIME_SEC", 60))

    domains_file = file_utils.read_lines(domains_file)

    preference_ext = file_utils.read_json(preference_file, default=[])
    
    # Executar processamento
    # Conta as extensões e organiza conforme preferências, salvando em arquivo para evitar reprocessamento
    counter_ext = ext_utils.count_by_extension(domains_file)
    selected = ext_utils.extension_organize(counter_ext, preference_ext, extensions_file)
    # Extrai apenas as extensões preferenciais para filtrar os domínios válidos que quer trabalhar
    selected_ext = [item.ext for item in selected.extensions]

    # Filtros aplicados sequencialmente para organizar os domínios
    filter_extension = build_domains(domains_file, selected_ext)
    filter_with_numbers, filter_without_numbers = numbers_filter(filter_extension)
    filter_long, filter_short = size_filter(filter_without_numbers, selected_ext, char_limit=size_domains)
    domains_with_special_chars, domains_clean = special_chars_filter(filter_short, selected_ext)
    
    print(f"✓ Domínios longos > {size_domains}: {len(filter_long)}")
    print(f"✓ Domínios com caracteres especiais: {len(domains_with_special_chars)}")
    print(f"✓ Domínios com números: {len(filter_with_numbers)}")
    print(f"===================================")
    print(f"✓ Total removidos: {len(filter_extension) - len(domains_clean)}")
    print(f"===================================")
    print(f"✓ Total de domínios brutos: {len(filter_extension)}")
    print(f"✓ Total de domínios para análise: {len(domains_clean)}")
    print(f"")

    file_names = []
    batches = split_into_batches(domains_clean, batch_size=chunk_size)
    for ibatch, batch in enumerate(batches):
        name_output = f"{dir_batches}/{file_utils.generate_filename(f'batch_{ibatch+1}', 'jsonl')}"
        file_utils.to_upload(batch, f"{name_output}")
        file_names.append(name_output)
    print(f"{len(batches)} Arquivos preparados em: {dir_batches}\n")

    for name in file_names: print(f"✓ {name}\n")
    
    if(await_option):
        print("Processando arquivos com OpenAI API ...")
        to_step_by_step_processing(file_names, interval_check=time_wait)
    else:
        print("Processamento com OpenAI API no modo bruto!")
        to_send_batch_openai(file_names)