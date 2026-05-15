from dotenv import load_dotenv
import os
from typing import List

from utils.domains import build_domains, numbers_filter, size_filter, special_chars_filter
import utils.files as file_utils
import utils.extensions as ext_utils

# from utils.api_processor import process_domains_sync, consolidate_results

load_dotenv()
    
if __name__ == "__main__":
    
    # Caminho do arquivo com os domínios
    domains_file = os.getenv("DOMAIN_LIST_FILE", "domains.txt")
    extensions_file = os.getenv("DOMAIN_EXTENSIONS", "domain_types.json")
    preference_file = os.getenv("DOMAIN_PREF_EXTENSIONS", "preference.json")
    domains_size = 16

    domains_file = file_utils.read_lines(domains_file)
    preference_ext = file_utils.read_json(preference_file, default=[])

    # Sistema de mensagem (customizar conforme necessário)
    system_msg = f"""Analise os domínios abaixo e retorne APENAS um JSON array.
                  Para cada domínio, avalie de 0-10: clareza, potencial comercial, memorabilidade.
                  Formato: [{{"dominio": "...", "nota": 7, "categoria": "ecommerce", "observacao": "..."}}]
                  Retorne SOMENTE o JSON, sem explicação."""
    
    # Executar processamento
    # Conta as extensões e organiza conforme preferências, salvando em arquivo para evitar reprocessamento
    counter_ext = ext_utils.count_by_extension(domains_file)
    selected = ext_utils.extension_organize(counter_ext, preference_ext, extensions_file)
    # Extrai apenas as extensões preferenciais para filtrar os domínios válidos que quer trabalhar
    selected_ext = [item.ext for item in selected.extensions]

    # Filtros aplicados sequencialmente para organizar os domínios
    filter_extension = build_domains(domains_file, selected_ext)
    filter_with_numbers, filter_without_numbers = numbers_filter(filter_extension)
    filter_long, filter_short = size_filter(filter_without_numbers, selected_ext, char_limit=domains_size)
    domains_with_special_chars, domains_clean = special_chars_filter(filter_short, selected_ext)
    
    print(f"✓ Domínios longos > {domains_size}: {len(filter_long)}")
    print(f"✓ Domínios com caracteres especiais: {len(domains_with_special_chars)}")
    print(f"✓ Domínios com números: {len(filter_with_numbers)}")
    print(f"===================================")
    print(f"✓ Total removidos: {len(filter_extension) - len(domains_clean)}")
    print(f"===================================")
    print(f"✓ Total de domínios brutos: {len(filter_extension)}")
    print(f"✓ Total de domínios para análise: {len(domains_clean)}")
    print(f"")

    # domains_list = [d.domain for d in domains_clean]

    # output_dir = "files"

    # api_url = "http://localhost:8000/services"
    # results = process_domains_sync(
    #     domains=domains_list,           # lista de dominios
    #     api_url=api_url,
    #     batch_size=50,                   # max 50 dominios por chamada
    #     workers=4,                       # max 4 requisicoes paralelas
    #     output_dir=output_dir             # diretorio para salvar JSONs
    # )
    # # Consolida tudo em um arquivo
    # consolidated_file = consolidate_results(results, output_dir)
    # print(f"Resultados consolidados em: {consolidated_file}")