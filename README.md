# Avaliador de Domínios em Batch

Utilitário em Python para preparar solicitações de avaliação de domínios, enviar para a OpenAI Batch API e baixar os resultados em JSONL.

## O que este projeto faz

- Lê domínios de um arquivo texto.
- Aplica etapas de análise e filtro (números, caracteres especiais, tamanho, agrupamento por extensão).
- Gera arquivos JSONL no formato aceito pela OpenAI Batch API.
- Faz upload dos JSONL e cria os batches.
- Consulta status dos batches e baixa resultados finalizados.

## Estrutura do projeto

- `main.py`: prepara os lotes e envia para a OpenAI.
- `batch_status.py`: verifica IDs de batch existentes e baixa saídas concluídas.
- `prepare_files.py`: integração com Batch API (upload/criação/status/download).
- `prompt_template.py`: prompts usados para pontuação dos domínios.
- `utils/domains.py`: parsing de domínio e filtros.
- `utils/extensions.py`: contagem e organização de extensões.
- `utils/files.py`: utilitários de leitura/escrita JSON e JSONL.
- `files/`: dados de entrada, batches gerados e resultados baixados.

## Requisitos

- Python 3.10+
- Chave de API OpenAI com acesso à Batch API

Instalação:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install openai
```

Observação: `prepare_files.py` importa `openai`, mas `openai` não está listado em `requirements.txt` neste momento.

## Configuração

Crie um `.env` (baseado em `.env.example`) com:

```env
API_KEY=sua_openai_api_key
WORKERS=4
CHUNK_SIZE=100
DOMAIN_EXTENSIONS="files/registro.br/extensions_20260408_20260415.json"
DOMAIN_LIST_FILE="files/registro.br/domains_20260408_20260415.txt"
DOMAIN_PREF_EXTENSIONS="files/preferences.json"
API_URL=http://127.0.0.1:8000/services
```

Importante:

- `API_KEY` é obrigatório para chamadas à OpenAI.
- `API_URL` não é usado no fluxo atual de batch, mas pode permanecer no `.env`.

## Formato de entrada

- Arquivo de domínios: texto puro, um domínio por linha.
- Linhas vazias e comentários iniciados por `#` são ignorados.

Exemplo:

```txt
example.com.br
meudominio.adv.br
```

## Execução do fluxo

### 1) Preparar e enviar batches

```bash
python main.py
```

O que acontece:

- Os domínios são lidos e analisados.
- Arquivos JSONL de request são gerados em `files/batches/`.
- Os arquivos são enviados para a OpenAI.
- Batches são criados e os IDs (`batch_id`) aparecem no terminal.

### 2) Consultar status e baixar resultados

Edite `batch_status.py` e preencha `files_list` com os IDs dos batches, depois rode:

```bash
python batch_status.py
```

Quando o batch estiver `completed`, a saída JSONL será salva em:

- `files/outputs/<batch_id>.jsonl`

## Formato de saída

Cada linha do JSONL de saída é um objeto retornado pela Batch API. O conteúdo da avaliação costuma estar em:

- `response.body.choices[0].message.content`

Esse campo normalmente contém uma string JSON gerada pelo modelo.

## Observações e comportamentos conhecidos

- O conteúdo baixado pode vir em bytes; `utils/files.py::write_jsonl` já decodifica para UTF-8 antes de escrever.
- Em `main.py`, os batches enviados são montados a partir da lista completa carregada (`domains_file`) após a impressão dos filtros. Se a intenção for enviar apenas os domínios filtrados, essa parte deve ser ajustada.

## Solução de problemas

- `TypeError: write() argument must be str, not bytes`
  - Resolvido ao decodificar bytes antes da escrita em `write_jsonl`.
- `ModuleNotFoundError: No module named 'openai'`
  - Instale com `pip install openai`.
- Arquivo de saída vazio
  - Verifique se o batch está `completed` e se possui `output_file_id`.

## Licença

Não há arquivo de licença incluído no momento.
