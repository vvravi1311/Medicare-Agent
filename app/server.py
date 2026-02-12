from pprint import pprint

from fastapi import FastAPI

# project imports
from .medicare_agent_graph import run_graph
from .server_models import InvokeRequest

app = FastAPI(title="Medicare Agent", version="1.0.0")


@app.get("/health")
def health():
    return {"status": "okk"}


@app.post("/medicare-agent")
def medicare_agent(request: InvokeRequest):
    # config = {"configurable": {"thread_id": request.thread_id or "default"}}
    result = run_graph(request)
    # final = result["messages"][-1].content
    pprint(result)
    return {"output": result}
