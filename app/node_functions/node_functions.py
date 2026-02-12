from langchain_core.messages import ToolMessage
import json

# project internal imports
from app.node_functions.mcp_tools import uw_chain, product_rag_chain
from app.node_functions.chains.categorize_chain import categorize_chain
from app.node_functions.chains.product_chain import product_grounding_chain

# from app.node_functions.mcp_tools import
from app.node_functions.chains.tools.models.constants import LAST, FIRST, MCP_SERVER_URL
from app.node_functions.chains.tools.models.state_graph_models import (
    MedicareMessageGraph,
    GroundingAgentResponse,
)
from app.node_functions.chains.judge_content import judge_chain

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

def categorize_agent_reason(state: MedicareMessageGraph):
    response = categorize_chain.invoke({"categorize_messages": state["messages"]})
    if response.content != "ELIGIBILITY_UNDERWRITING" or response.content != "PRODUCT":
        final_answer = "The query is not a Medicare related query, Ican only answer medicare related queries"
        return {
            "messages": [response],
            "agent_category": response.content,
            "user_query": state["messages"][FIRST].content,
            "final_answer": final_answer,
        }
    return {
        "messages": [response],
        "agent_category": response.content,
        "user_query": state["messages"][FIRST].content,
    }


def product_agent_reason(state: MedicareMessageGraph):
    response = product_rag_chain.invoke({"product_rag_messages": state["messages"]})
    if isinstance(state["messages"][LAST], ToolMessage):
        answer = response.content
        audit = []
        for artifact in json.loads(
            json.loads(state["messages"][LAST].content)["result"]["content"][LAST][
                "text"
            ]
        ):
            audit.append(
                {
                    "source": artifact["metadata"]["source"],
                    "page_number": artifact["metadata"]["MY_page_number"],
                }
            )
        return {
            "messages": [response],
            "final_answer": response.content,
            "product_response": {"answer": response.content, "audit": audit},
        }  # When the product agent responds with final answer
    return {
        "messages": [response]
    }  # first time when the agent decides to call the tool


def judge_reason(state: MedicareMessageGraph):
    question = state.get("user_query")
    context = ""
    if isinstance(state["messages"][LAST], ToolMessage):
        context = json.loads(state["messages"][LAST].content)["result"]["content"][0][
            "text"
        ]
    result = judge_chain.invoke({"question": question, "context": context})
    if int(result.score) <= 3:
        return {
            "judge_evaluation_score": result.score,
            "final_answer": result.evaluation,
        }
    else:
        return {"judge_evaluation_score": result.score}


def uw_agent_reason(state: MedicareMessageGraph):
    response = uw_chain.invoke({"uw_messages": state["uw_agent_messages"]})
    answer = response.content
    if isinstance(state["uw_agent_messages"][LAST], ToolMessage):
        answer = response.content
        audit = {}
        audit = json.loads(json.loads(state["uw_agent_messages"][LAST].content)["result"]["content"][0]["text"])["audit"]
        return {
            "uw_agent_messages": [response],
            "final_answer": response.content,
            "underwriting_response": {
                "answer": response.content,
                "audit": [{"audit_info": audit}],
            },
        }
    return {"uw_agent_messages": [response]}

def product_grounding_reason(state: MedicareMessageGraph):
    question = state.get("user_query")
    answer = state.get("messages")[LAST].content
    context = ""
    if has_tool_message(state.get("messages")):
        tool_msg = next(
            msg for msg in state["messages"] if isinstance(msg, ToolMessage)
        )
        context = tool_msg.content
    print(question, answer, context)
    result = product_grounding_chain.invoke(
        {"question": state["messages"], "context": context, "answer": answer}
    )
    return {
        "grounding_agent_response": {
            "is_grounded": result.is_grounded,
            "grounding_agent_answer": result.grounding_agent_answer,
        }
    }
