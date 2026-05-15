# utils/api_processor.py
import asyncio
import aiohttp
import json
from pathlib import Path
from datetime import datetime
from typing import List

from prompt_template import get_prompt_domains

async def call_api(session, api_url, batch, semaphore):
    """Chama API com controle de concorrencia"""
    async with semaphore:
        try:
            payload = get_prompt_domains(batch)
            async with session.post(api_url, json=payload, timeout=aiohttp.ClientTimeout(total=3000)) as response:
                if response.status == 200:
                    return {
                        "batch": batch,
                        "status": "success",
                        "result": await response.json(),
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    return {"batch": batch, "status": "error", "error": f"HTTP {response.status}", "timestamp": datetime.now().isoformat()}
        except Exception as e:
            return {"batch": batch, "status": "error", "error": str(e), "timestamp": datetime.now().isoformat()}

def split_into_batches(domains: List[str], batch_size: int) -> List[List[str]]:
    """Divide dominios em batches"""
    return [domains[i:i + batch_size] for i in range(0, len(domains), batch_size)]

def save_result_to_file(result: dict, output_dir: str = "results") -> str:
    """Salva cada resultado em arquivo JSON"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    batch = result.get("batch", [])
    first_domain = batch[0].replace(".", "_") if batch else "batch"
    timestamp = result.get("timestamp", datetime.now().isoformat()).replace(":", "-")
    filename = f"{first_domain}_{timestamp}.json"
    
    file_path = output_path / filename
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    return str(file_path)

async def process_domains_async(domains, api_url, batch_size=50, workers=4, output_dir="results"):
    """Processa dominios em batches com requisicoes paralelas"""
    batches = split_into_batches(domains, batch_size)
    semaphore = asyncio.Semaphore(workers)
    results = []
    
    async with aiohttp.ClientSession() as session:
        tasks = [call_api(session, api_url, batch, semaphore) for batch in batches]
        responses = await asyncio.gather(*tasks)
    
    for response in responses:
        file_path = save_result_to_file(response, output_dir)
        response["file_path"] = file_path
        results.append(response)
        print(f"Salvo: {file_path}")
    
    return results

def process_domains_sync(domains, api_url, batch_size=50, workers=4, output_dir="results"):
    """Wrapper sincrono"""
    return asyncio.run(process_domains_async(domains, api_url, batch_size, workers, output_dir))

def consolidate_results(results, output_file="results/consolidated.json"):
    """Consolida todos os resultados"""
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    summary = {
        "total_batches": len(results),
        "successful": sum(1 for r in results if r.get("status") == "success"),
        "failed": sum(1 for r in results if r.get("status") == "error"),
        "results": results,
        "timestamp": datetime.now().isoformat()
    }
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    return str(output_path)