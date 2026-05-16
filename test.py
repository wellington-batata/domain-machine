import json
import time
from openai import OpenAI

client = OpenAI(api_key="")

# ─── 1. Seus domínios a categorizar ───────────────────────────────────────────
dominios = [
    "globo.com",
    "mercadolivre.com.br",
    "uol.com.br",
    "ifood.com.br",
    "nubank.com.br",
]

CATEGORIAS = "Notícias, E-commerce, Entretenimento, Finanças, Tecnologia, Educação, Saúde, Outro"

# ─── 2. Montar o arquivo JSONL ─────────────────────────────────────────────────
linhas = []
for i, dominio in enumerate(dominios):
    linha = {
        "custom_id": f"dominio-{i}",  # ID único para mapear depois
        "method": "POST",
        "url": "/v1/chat/completions",
        "body": {
            "model": "gpt-4o-mini",
            "max_tokens": 50,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        f"Você é um classificador de domínios. "
                        f"Responda APENAS com uma das categorias: {CATEGORIAS}. "
                        f"Sem explicações."
                    )
                },
                {
                    "role": "user",
                    "content": f"Categorize o domínio: {dominio}"
                }
            ]
        }
    }
    linhas.append(json.dumps(linha))

# Salvar o arquivo localmente
with open("batch_dominios.jsonl", "w") as f:
    f.write("\n".join(linhas))

print(f"Arquivo criado com {len(linhas)} requisições.")

# ─── 3. Upload do arquivo ──────────────────────────────────────────────────────
with open("batch_dominios.jsonl", "rb") as f:
    arquivo = client.files.create(file=f, purpose="batch")

print(f"Arquivo enviado. file_id: {arquivo.id}")

# ─── 4. Criar o batch ──────────────────────────────────────────────────────────
batch = client.batches.create(
    input_file_id=arquivo.id,
    endpoint="/v1/chat/completions",
    completion_window="24h",
    metadata={"descricao": "Categorização de domínios"}
)

print(f"Batch criado. batch_id: {batch.id} | status: {batch.status}")

# ─── 5. Aguardar conclusão (polling) ───────────────────────────────────────────
print("Aguardando conclusão...")
while True:
    batch = client.batches.retrieve(batch.id)
    print(f"  Status: {batch.status} | "
          f"Completos: {batch.request_counts.completed}/{batch.request_counts.total}")

    if batch.status in ("completed", "failed", "expired", "cancelled"):
        break

    time.sleep(30)  # Verifica a cada 30 segundos

# ─── 6. Baixar e processar resultados ─────────────────────────────────────────
if batch.status == "completed":
    conteudo = client.files.content(batch.output_file_id).text

    # Mapear custom_id -> domínio original
    mapa = {f"dominio-{i}": d for i, d in enumerate(dominios)}

    print("\n── Resultados ──────────────────────────")
    for linha in conteudo.strip().split("\n"):
        resultado = json.loads(linha)
        custom_id = resultado["custom_id"]
        dominio = mapa[custom_id]
        categoria = resultado["response"]["body"]["choices"][0]["message"]["content"].strip()
        print(f"{dominio:30s} → {categoria}")
else:
    print(f"Batch encerrou com status: {batch.status}")
    # Checar erros
    if batch.error_file_id:
        erros = client.files.content(batch.error_file_id).text
        print("Erros:\n", erros)