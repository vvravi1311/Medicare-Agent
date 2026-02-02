from typing import TypedDict, Annotated, Any, Dict, Optional
from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage, AIMessage
from langgraph.graph.message import add_messages
from dotenv import load_dotenv
from langgraph.graph import MessagesState, StateGraph,END
from langgraph.prebuilt import ToolNode
import json

# project internal imports
from app.node_functions.chains.uw_chain import uw_chain
from app.node_functions.chains.categorize_chain import categorize_chain
from app.node_functions.chains.tools.tools import uw_tools
from app.node_functions.chains.tools.models.constants import LAST,FIRST

# class MessageGraph(TypedDict):
#     messages: Annotated[list[BaseMessage], add_messages]

class MedicareMessageGraph(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    # Input from the user
    user_query: Optional[str]
    error_message: Optional[str]
    # Output from the categorizer
    agent_category: Optional[str]
    # Output from the product agent
    product_response: Optional[str]
    # Output from the eligibility/underwriting agent
    underwriting_response: Optional[str]

def categorize_agent_reason(state: MedicareMessageGraph):
    response = categorize_chain.invoke({"categorize_messages": state["messages"]})
    return {"messages": [response],"agent_category":response.content, "user_query":state["messages"][FIRST].content }

def product_agent_reason(state: MedicareMessageGraph):
    # add product code here
    return {"messages": [AIMessage(content="this is a mock, need to include the RAG agent call")]}

def uw_agent_reason(state: MedicareMessageGraph):
    # write code to update the agent response in the State Message
    return {"messages": [uw_chain.invoke({"uw_messages": state["messages"]})]}

# defining the tool_nodes
uw_tool_node = ToolNode(uw_tools)