from typing import TypedDict, Annotated, Any, Dict
from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
from langgraph.graph import MessagesState, StateGraph,END
from langgraph.prebuilt import ToolNode
import json

# project internal imports
from app.node_functions.chains.uw_chain import uw_chain
from app.node_functions.chains.tools.tools import uw_tools

class MessageGraph(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def uw_agent_reason(state: MessageGraph):
    return {"messages": [uw_chain.invoke({"uw_messages": state["messages"]})]}


# defining the tool_nodes
uw_tool_node = ToolNode(uw_tools)