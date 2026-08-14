from typing import Any
from pydantic import BaseModel

class GeneratorResponse(BaseModel):
    total_records: int
    chaos_enabled: bool
    data: list[dict[str, Any]]