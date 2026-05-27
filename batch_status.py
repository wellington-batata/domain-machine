from dotenv import load_dotenv
import os

import openai_client

load_dotenv()

raw_batch_ids = os.getenv("BATCH_IDS", "")
files_list = [batch_id.strip() for batch_id in raw_batch_ids.split(",") if batch_id.strip()]

if not files_list:
	raise ValueError("Defina BATCH_IDS no ambiente com IDs separados por vírgula.")

openai_client.to_check_status_batch_openai(files_list)