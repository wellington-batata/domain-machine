import asyncio
import aiohttp
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

from dotenv import load_dotenv
import os
from typing import List

from utils.domains import separate_domains_with_numbers, separate_domains_by_special_chars, filter_long_domains
import utils.files as file_utils
import utils.extensions as ext_utils

from schemas import Domain, Extensions, ExtensionItem

load_dotenv()

# async def call_api(session: aiohttp.ClientSession, system_message: str, message: str, semaphore: asyncio.Semaphore) -> dict:
#     """
#     Chama a API no endereço http://127.0.0.1:8000
    
#     Args:
#         session: Sessão aiohttp
#         system_message: Mensagem do sistema
#         message: Mensagem a enviar
        
#     Returns:
#         Resposta da API em formato dict
#     """
#     url = os.getenv("API_URL", "http://localhost:8000/services")

#     payload = {
#         "system_message": system_message,
#         "message": message
#     }
    
#     try:
#         async with semaphore:
#             async with session.post(url, json=payload, timeout=aiohttp.ClientTimeout(total=300)) as response:
#                 print(f"Chamando API para: {message} - Status: {response.status}")
#                 return await response.json()
#     except Exception as e:
#         return {"error": str(e), "message": message}


# async def process_domains_from_file(filepath: str, system_message: str = "") -> List[dict]:

#     # Ler domínios do arquivo
#     try:
#         with open(filepath, 'r', encoding='utf-8') as f:
#             domains = [line.strip() for line in f if line.strip()]
#     except FileNotFoundError:
#         print(f"Arquivo não encontrado: {filepath}")
#         return []
    
#     if not domains:
#         print("Nenhum domínio encontrado no arquivo")
#         return []
    
#     # Criar sessão e limitar concorrência a 4 chamadas simultâneas
#     semaphore = asyncio.Semaphore(4)
#     async with aiohttp.ClientSession() as session:
#         tasks = [
#             call_api(session, system_message, domain, semaphore)
#             for domain in domains
#         ]
#         results = await asyncio.gather(*tasks)
#     return results

# def analisar_lote(lote_id: int, dominios: list[str]) -> list[dict]:
#     texto = dominios["message"]["content"]
#     inicio, fim = texto.find("["), texto.rfind("]") + 1
#     dados = json.loads(texto[inicio:fim])
#     print(f"✓ Lote {lote_id} concluído ({len(dados)} domínios)")
#     return dados

    
# def processar_tudo(arquivo: str, chunk=50, workers=4):
#     dominios = [line for line in open(arquivo).read().splitlines() if not line.startswith("#")]
#     lotes = [dominios[i:i+chunk] for i in range(0, len(dominios), chunk)]
#     todos = []
#     name = arquivo.split(".")[0]
#     domain_type = f"{name}_types.json"
#     list_domains_type(arquivo, domain_type)
                
# def process_domains_sync(filepath: str, system_message: str = "") -> List[dict]:
#     chunk_size = int(os.getenv("CHUNK_SIZE", 100))
#     workers = int(os.getenv("WORKERS", 4))
#     return processar_tudo(filepath, chunk=chunk_size, workers=workers)


    #return asyncio.run(process_domains_from_file(filepath, system_message))



def extension_organize(extensions: dict[str, int], preference_ext: list[str], ext_type_file: str) -> Extensions:

    if os.path.exists(ext_type_file):
        data = file_utils.read_json(ext_type_file, default={"extensions": [], "ignored": []})
        return Extensions(**data)
    else:
        ext_types = ext_utils.extract_extensions(extensions, preference_ext)
        file_utils.write_json(ext_type_file, ext_types.model_dump(), indent=2)
        return ext_types
    
def count_by_extension(domains: list[str]) -> dict[str, int]:
    ext_counts = {}
    for domain in domains:
        ext = ext_utils.get_extension(domain)
        if ext:
            ext_counts[ext] = ext_counts.get(ext, 0) + 1
    
    return [{"ext": k, "count": v} for k, v in ext_counts.items()]


if __name__ == "__main__":
    
    # Caminho do arquivo com os domínios
    domains_file = os.getenv("DOMAIN_LIST_FILE", "domains.txt")
    extensions_file = os.getenv("DOMAIN_EXTENSIONS", "domain_types.json")
    preference_file = os.getenv("DOMAIN_PREF_EXTENSIONS", "preference.json")
    domains_size = 17

    domains = file_utils.read_lines(domains_file)
    preference_ext = file_utils.read_json(preference_file, default=[])

    # Sistema de mensagem (customizar conforme necessário)
    system_msg = f"""Analise os domínios abaixo e retorne APENAS um JSON array.
                  Para cada domínio, avalie de 0-10: clareza, potencial comercial, memorabilidade.
                  Formato: [{{"dominio": "...", "nota": 7, "categoria": "ecommerce", "observacao": "..."}}]
                  Retorne SOMENTE o JSON, sem explicação."""
    
    # Executar processamento
    # Conta as extensões e organiza conforme preferências, salvando em arquivo para evitar reprocessamento
    counter_ext = count_by_extension(domains)
    organized_ext = extension_organize(counter_ext, preference_ext, extensions_file)
    # Extrai apenas as extensões preferenciais para filtrar os domínios válidos que quer trabalhar
    only_ext = [item.ext for item in organized_ext.extensions]

    # Filtra da lista original apenas os domínios que possuem as extensões preferenciais
    filtered_domains = ext_utils.filter_by_extensions(domains, only_ext)
    # Separa domínios com números e sem números
    domains_with_numbers, domains_without_numbers = separate_domains_with_numbers(filtered_domains)

    long_domains, short_domains = filter_long_domains(domains_without_numbers, only_ext, char_limit=domains_size)
    domains_with_special_chars, domains_clean = separate_domains_by_special_chars(short_domains, only_ext)



    print(f"✓ Domínios NÃO preferenciais: {len(domains) - len(filtered_domains)}")
    print(f"✓ Domínios longos >{domains_size}: {len(long_domains)}")
    print(f"✓ Domínios com números: {len(domains_with_numbers)}")
    print(f"")
    print(f"✓ Total de domínios brutos: {len(domains)}")
    print(f"✓ Total de domínios filtrados: {len(domains_clean)}")
    print(f"")
    
    # print(f"✓ Domínios com extensões preferenciais: {len(filtered_domains)}")
    # print(f"✓ Domínios sem números: {len(domains_without_numbers)}")
    # print(f"✓ Domínios com caracteres especiais: {len(domains_with_special_chars)}")
    # print(f"✓ Domínios limpos: {len(domains_clean)}")
    # print(f"✓ Domínios curtos <{domains_size}: {len(short_domains)}")

    # removed_domains = set(domains) - set(filtered_domains)
    # print(f"✓ Domínios removidos: {len(removed_domains)}")

    # Exibir resultados
    # print(json.dumps(organized_ext.model_dump().get("extensions", []), indent=2, ensure_ascii=False))
