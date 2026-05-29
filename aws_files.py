import os

import boto3
from botocore.exceptions import BotoCoreError, ClientError


def create_s3_client(
	region_name: str | None = None,
	aws_access_key_id: str | None = None,
	aws_secret_access_key: str | None = None,
):
	"""
	Cria um cliente S3 usando credenciais explícitas (quando fornecidas)
	ou variáveis de ambiente/perfil AWS configurado.
	"""
	region = region_name or os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION")
	access_key = aws_access_key_id or os.getenv("AWS_ACCESS_KEY_ID")
	secret_key = aws_secret_access_key or os.getenv("AWS_SECRET_ACCESS_KEY")

	client_args: dict[str, str] = {}
	if region:
		client_args["region_name"] = region
	if access_key and secret_key:
		client_args["aws_access_key_id"] = access_key
		client_args["aws_secret_access_key"] = secret_key

	return boto3.client("s3", **client_args)


def list_files_s3(
	bucket_name: str,
	prefix: str = ""
) -> list[str]:
	"""
	Lista arquivos de um bucket S3, opcionalmente filtrando por prefixo.
	"""
	s3 = create_s3_client()
	paginator = s3.get_paginator("list_objects_v2")

	files: list[str] = []
	try:
		for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix):
			for item in page.get("Contents", []):
				key = item.get("Key")
				if key and not key.endswith("/"):
					files.append(key)
	except (ClientError, BotoCoreError) as exc:
		raise RuntimeError(f"Erro ao listar arquivos no bucket '{bucket_name}': {exc}") from exc

	return files


def create_file_s3(
	bucket_name: str,
	key: str,
	content: str | bytes = "",
	content_type: str | None = None
) -> str:
	"""
	Cria um arquivo no S3 (ou sobrescreve se já existir) a partir de conteúdo em memória.
	Retorna a chave do objeto criado.
	"""
	s3 = create_s3_client()

	body = content.encode("utf-8") if isinstance(content, str) else content

	put_args = {
		"Bucket": bucket_name,
		"Key": key,
		"Body": body,
	}
	if content_type:
		put_args["ContentType"] = content_type

	try:
		s3.put_object(**put_args)
	except (ClientError, BotoCoreError) as exc:
		raise RuntimeError(f"Erro ao criar arquivo '{key}' no bucket '{bucket_name}': {exc}") from exc

	return key


def upload_file_to_s3(
	local_file_path: str,
	bucket_name: str,
	key: str
) -> str:
	"""
	Faz upload de um arquivo local para o S3.
	Retorna a chave do objeto criado.
	"""
	s3 = create_s3_client()

	try:
		s3.upload_file(local_file_path, bucket_name, key)
	except (ClientError, BotoCoreError, FileNotFoundError) as exc:
		raise RuntimeError(
			f"Erro ao enviar arquivo local '{local_file_path}' para '{bucket_name}/{key}': {exc}"
		) from exc

	return key


def download_file_from_s3(
	bucket_name: str,
	key: str,
	local_file_path: str
) -> str:
	"""
	Baixa um arquivo do S3 para um caminho local.
	Retorna o caminho local do arquivo baixado.
	"""
	s3 = create_s3_client()
	local_dir = os.path.dirname(local_file_path)
	if local_dir:
		os.makedirs(local_dir, exist_ok=True)

	try:
		s3.download_file(bucket_name, key, local_file_path)
	except (ClientError, BotoCoreError) as exc:
		raise RuntimeError(
			f"Erro ao baixar arquivo '{bucket_name}/{key}' para '{local_file_path}': {exc}"
		) from exc

	return local_file_path


def delete_file_or_folder_s3(
	bucket_name: str,
	path: str
) -> int:
	"""
	Deleta um arquivo (key exata) ou uma pasta lógica (prefixo) no S3.
	- Se path terminar com "/", remove todos os objetos sob esse prefixo.
	- Caso contrário, remove apenas a key informada.
	Retorna a quantidade de objetos removidos.
	"""
	s3 = create_s3_client()

	if not path:
		raise ValueError("'path' não pode ser vazio.")

	try:
		if path.endswith("/"):
			paginator = s3.get_paginator("list_objects_v2")
			keys_to_delete: list[dict[str, str]] = []

			for page in paginator.paginate(Bucket=bucket_name, Prefix=path):
				for item in page.get("Contents", []):
					key = item.get("Key")
					if key:
						keys_to_delete.append({"Key": key})

			if not keys_to_delete:
				return 0

			deleted_count = 0
			chunk_size = 1000
			for i in range(0, len(keys_to_delete), chunk_size):
				chunk = keys_to_delete[i:i + chunk_size]
				response = s3.delete_objects(Bucket=bucket_name, Delete={"Objects": chunk})
				deleted_count += len(response.get("Deleted", []))

			return deleted_count

		s3.delete_object(Bucket=bucket_name, Key=path)
		return 1
	except (ClientError, BotoCoreError) as exc:
		raise RuntimeError(
			f"Erro ao deletar '{path}' no bucket '{bucket_name}': {exc}"
		) from exc
