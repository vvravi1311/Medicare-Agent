from typing import TypedDict, Annotated, Any, Dict, Optional,List

from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage, AIMessage
from langgraph.graph.message import add_messages
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

# class MessageGraph(TypedDict):
#     messages: Annotated[list[BaseMessage], add_messages]

class Audit(BaseModel):
    source:Optional[str]
    page_number:Optional[str]
class ProductAgentResponse(BaseModel):
    answer: Optional[str] = ""
    audit: Optional[List[Audit]] = Field(default_factory=list)
class MedicareMessageGraph(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    # Input from the user
    user_query: Optional[str]
    error_message: Optional[str]
    # Output from the categorizer
    agent_category: Optional[str]
    # Output from the product agent
    product_response: Optional[ProductAgentResponse]
    # Output from the eligibility/underwriting agent
    underwriting_response: Optional[str]

def categorize_agent_reason(state: MedicareMessageGraph):
    response = categorize_chain.invoke({"categorize_messages": state["messages"]})
    return {"messages": [response],"agent_category":response.content, "user_query":state["messages"][FIRST].content }

def product_agent_reason(state: MedicareMessageGraph):
    response = product_rag_chain.invoke({"product_rag_messages": state["messages"]})
    if isinstance(state["messages"][LAST], ToolMessage):
        aa = ProductAgentResponse()
        aa.answer = response.content
        # aa.audit = [{
        #         "source": "source",
        #         "page_number": "MY_page_number"
        #     }]
        # state["product_response"] = "not there yet"
        for artifact in state["messages"][LAST].artifact:
            aa.audit.append({
                "source": artifact.metadata["source"],
                "page_number": artifact.metadata["MY_page_number"]
            })
        return {"messages": [product_rag_chain.invoke({"product_rag_messages": state["messages"]})],
                "product_response": aa}

    return {"messages": [product_rag_chain.invoke({"product_rag_messages": state["messages"]})]}

def uw_agent_reason(state: MedicareMessageGraph):
    # write code to update the agent response in the State Message
    return {"messages": [uw_chain.invoke({"uw_messages": state["messages"]})]}


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
    result = [product_grounding_chain.invoke({
            "question": state["messages"],
            "context": context,
            "answer": answer})]
    return result
    # return {
    #     "messages": [product_grounding_chain.invoke({
    #         "question": state["messages"],
    #         "context": context,
    #         "answer": answer})]
    # }

# defining the tool_nodes
uw_tool_node = ToolNode(uw_tools)
product_tool_node=ToolNode(product_rag_tools)