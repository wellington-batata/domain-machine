import re

from datetime import datetime

def log_now():
    return datetime.now().strftime("%Y-%m-%d %H:%M")

def extract_date_registrobr(line: str) -> datetime | None:
    match = re.search(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', line)
    if match:
        dt = datetime.fromisoformat(match.group())
        return dt.strftime("%Y%m%d")  # "20260406"
    return None