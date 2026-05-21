from dotenv import load_dotenv
import os

import prepare_files as prepare_files

load_dotenv()

files_list = ['batch_6a0e4e03c0448190989efa410cc23914']

prepare_files.to_check_status_batch_openai(files_list)