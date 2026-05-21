from dotenv import load_dotenv
import os

from utils.domains import build_domains, numbers_filter, size_filter, special_chars_filter, split_into_batches
import utils.files as file_utils
import utils.extensions as ext_utils
import prepare_files as prepare_files
# from utils.api_processor import process_domains_sync, consolidate_results

load_dotenv()
    
if __name__ == "__main__":
    
    # Caminho do arquivo com os domínios
    domains_file = os.getenv("DOMAIN_LIST_FILE", "domains.txt")
    extensions_file = os.getenv("DOMAIN_EXTENSIONS", "domain_types.json")
    preference_file = os.getenv("DOMAIN_PREF_EXTENSIONS", "files/preference.json")
    dir_output = os.getenv("DIR_OUTPUT", "files/batches")
    chunk_size = int(os.getenv("CHUNK_SIZE", 20000))
    size_domains = 16

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
    batches = split_into_batches(domains_file, batch_size=chunk_size)
    for ibatch, batch in enumerate(batches):
        name_output = f"{dir_output}/{file_utils.generate_filename(f'batch_{ibatch+1}', 'jsonl')}"
        prepare_files.to_upload(batch, f"{name_output}")
        file_names.append(name_output)
    print(f"{len(batches)} Arquivos preparados em: {dir_output}\n")

    for name in file_names: print(f"✓ {name}\n")
    
    prepare_files.to_send_batch_openai(file_names)