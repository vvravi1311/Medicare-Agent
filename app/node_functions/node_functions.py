from typing import TypedDict, Annotated, Any, Dict, Optional,List

from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage, AIMessage

from dotenv import load_dotenv
from langgraph.graph import MessagesState, StateGraph,END
from langgraph.prebuilt import ToolNode
import json

# project internal imports
from app.node_functions.chains.uw_chain import uw_chain
from app.node_functions.chains.categorize_chain import categorize_chain
from app.node_functions.chains.product_chain import product_grounding_chain,product_rag_chain
from app.node_functions.chains.tools.tools import uw_tools,product_rag_tools
from app.node_functions.chains.tools.models.constants import LAST,FIRST
from app.node_functions.chains.tools.models.state_graph_models import MedicareMessageGraph,ProductAgentResponse,GroundingAgentResponse,AnyAgentResponse


def categorize_agent_reason(state: MedicareMessageGraph):
    response = categorize_chain.invoke({"categorize_messages": state["messages"]})
    return {"messages": [response],"agent_category":response.content, "user_query":state["messages"][FIRST].content }

def product_agent_reason(state: MedicareMessageGraph):
    response = product_rag_chain.invoke({"product_rag_messages": state["messages"]})
    if isinstance(state["messages"][LAST], ToolMessage):
        # product_agent_response = ProductAgentResponse()
        answer = response.content
        audit = []
        for artifact in state["messages"][LAST].artifact:
            audit.append({
                "source": artifact.metadata["source"],
                "page_number": artifact.metadata["MY_page_number"]
            })
        return {"messages": [response],
                "product_response":
                    {"answer":response.content,
                     "audit":audit}} # When the product agent responds with final answer
    return {"messages": [response]} # first time when the agent decides to call the tool

def uw_agent_reason(state: MedicareMessageGraph):
    response = uw_chain.invoke({"uw_messages": state["uw_agent_messages"]})
    answer = response.content
    if isinstance(state["uw_agent_messages"][LAST], ToolMessage):
        answer = response.content
        audit = {}
        audit = json.loads(state["uw_agent_messages"][LAST].content)["audit"]
        return {"uw_agent_messages": [response],
                "underwriting_response":
                    {"answer": response.content,
                     "audit":[{"audit_info": audit}]}}
    return {"uw_agent_messages": [response],
            "underwriting_response": {"answer": response.content, "audit": [{"dummy-audit": "some value"}]}}


def has_tool_message(result):
    # Case 1: result is a single message
    if hasattr(result, "tool_calls") and result.tool_calls:
        return True
    # Case 2: result is a dict with messages
    if isinstance(result, dict) and "messages" in result:
        for msg in result["messages"]:
            if getattr(msg, "type", None) == "tool":
                return True
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                return True
    return False

def product_grounding_reason(state: MedicareMessageGraph):
    question = state.get("user_query")
    answer = state.get("messages")[LAST].content
    context = ""
    if has_tool_message(state.get("messages")):
        tool_msg = next(msg for msg in state["messages"] if isinstance(msg, ToolMessage))
        context = tool_msg.content
    print("***********************      question, answer, context     *****************************")
    print(question, answer, context)
    result = product_grounding_chain.invoke({
            "question": state["messages"],
            "context": context,
            "answer": answer})
    grounding_answer = GroundingAgentResponse(
        is_grounded=result.is_grounded,
        grounding_agent_answer=result.grounding_agent_answer )
    # grounding_answer.is_grounded = result[0].is_grounded
    # grounding_answer.grounding_agent_answer = result[0].grounding_agent_answer
    return {"grounding_agent_response": grounding_answer}

# defining the tool_nodes
uw_tool_node = ToolNode(uw_tools,messages_key="uw_agent_messages")
product_tool_node=ToolNode(product_rag_tools)