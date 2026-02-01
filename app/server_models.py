from pydantic import BaseModel

class InvokeRequest(BaseModel):
    query: str
    thread_id: str | None = None