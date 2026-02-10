import os
import json
import requests
from langgraph.prebuilt import ToolNode
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# project imports
from app.node_functions.chains.product_chain import product_rag_prompt
from app.node_functions.chains.tools.models.constants import PRODUCT_AGENT_MODEL
load_dotenv()

MCP_SERVER_URL = "https://ld8gokydyk.execute-api.us-east-1.amazonaws.com/Prod/mcp/"
API_KEY = "L5M33bj1Dk6YfTDcn2xvE19u7faPnt9I1ElLMrNX"

# connect to MCP server and get all MCP tools
def get_mcp_tools():
    headers = {"x-api-key": API_KEY}
    response = requests.post(MCP_SERVER_URL, headers=headers, json={"method": "tools/list"})
    response.raise_for_status()
    data = response.json()
    return data["result"]["tools"]


# convert the MCP tools into Langchain tools
def create_langchain_tools():
    from langchain_core.tools import StructuredTool
    mcp_tools = get_mcp_tools()
    tools = []
    for mcp_tool in mcp_tools:
        tool_name = mcp_tool["name"]
        tool_desc = mcp_tool.get("description", "MCP tool")

        def make_tool(name, desc):
            def dynamic_tool(query: str) -> str:
                """Execute MCP tool"""
                headers = {"x-api-key": API_KEY}
                payload = {"method": "tools/call", "params": {"name": name, "arguments": {"query": query}}}
                response = requests.post(MCP_SERVER_URL, headers=headers, json=payload)
                return json.dumps(response.json())

            return StructuredTool.from_function(
                func=dynamic_tool,
                name=name,
                description=desc
            )

        tools.append(make_tool(tool_name, tool_desc))
    return tools

tools = create_langchain_tools()
product_tool_node = ToolNode(tools)

product_rag_llm = ChatOpenAI(model=PRODUCT_AGENT_MODEL, temperature=0).bind_tools(tools)
product_rag_chain = product_rag_prompt | product_rag_llm