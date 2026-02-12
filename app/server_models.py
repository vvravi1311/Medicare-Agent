from pydantic import BaseModel
from typing import Optional


class InvokeRequest(BaseModel):
    query: Optional[str] = ""
    thread_id: Optional[str] = ""
