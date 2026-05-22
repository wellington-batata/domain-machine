from pydantic import BaseModel, Field
from typing import Any

class ExtensionItem(BaseModel):
    ext: str
    count: int

class Extensions(BaseModel):
    extensions: list[ExtensionItem]
    ignored: list[ExtensionItem]

class DomainDetail(BaseModel):
    domain_name: str | None = None
    extension: str | None = None
    length: int | None = None
    has_numbers: bool | None = None
    has_special_chars: bool | None = None

class Domain(BaseModel):
    domain: str
    detail: DomainDetail | None = None

class OpenAI_Batch(BaseModel):
    batch_id: str
    file_id: str
    input_file_id: str