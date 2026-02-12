import json
import requests
from langgraph.prebuilt import ToolNode
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from langchain_core.messages import ToolMessage
from pydantic import BaseModel
from langchain_core.tools import StructuredTool

# project imports
from app.node_functions.chains.product_chain import product_rag_prompt
from app.node_functions.chains.uw_chain import uw_prompt
from app.node_functions.chains.tools.models.state_graph_models import RequestWrapper
from app.node_functions.chains.tools.models.constants import (
    PRODUCT_AGENT_MODEL,
    UW_AGENT_MODEL,
)

load_dotenv()

MCP_SERVER_URL = "https://piz1zc7qwl.execute-api.us-east-1.amazonaws.com/Prod/mcp"
API_KEY = "1uti3JeXeI8hC7dFcyD0naOALp9nEhLj74BqfyG0"


# connect to MCP server and get all MCP tools
def get_mcp_tools():
    headers = {"x-api-key": API_KEY}
    response = requests.post(
        MCP_SERVER_URL, headers=headers, json={"method": "tools/list"}
    )
    response.raise_for_status()
    data = response.json()
    return data["result"]["tools"]

def create_langchain_tools():
    mcp_tools = get_mcp_tools()
    tools = []

    for mcp_tool in mcp_tools:
        tool_name = mcp_tool["name"]
        tool_desc = mcp_tool.get("description", "MCP tool")

        def make_tool(name=tool_name, desc=tool_desc):

            def dynamic_tool(request: RequestWrapper) -> str:
                headers = {"x-api-key": API_KEY}
                payload = {
                    "method": "tools/call",
                    "params": {
                        "name": name,
                        "arguments": {
                            "request": request.dict(exclude_none=True)
                        }
                    }
                }
                response = requests.post(MCP_SERVER_URL, headers=headers, json=payload)
                return json.dumps(response.json())

            return StructuredTool.from_function(
                func=dynamic_tool,
                name=name,
                description=desc
            )

        tools.append(make_tool())

    return tools
tools = create_langchain_tools()
product_tool_node = ToolNode(tools)
print(f"Tools loaded: {len(tools)}")

product_rag_llm = ChatOpenAI(model=PRODUCT_AGENT_MODEL, temperature=0).bind_tools(tools)
product_rag_chain = product_rag_prompt | product_rag_llm


uw_tool_node = ToolNode(tools, messages_key="uw_agent_messages")
uw_llm = ChatOpenAI(model=UW_AGENT_MODEL, temperature=0).bind_tools(tools)
uw_chain = uw_prompt | uw_llm
