from typing import TypedDict, Annotated, Any, Dict, Optional
from pprint import pprint

from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage

from langgraph.graph import MessagesState, StateGraph,END
from langgraph.graph.message import add_messages

# project internal imports
from app.node_functions.node_functions import uw_agent_reason,MedicareMessageGraph,categorize_agent_reason,product_agent_reason,product_grounding_reason
from app.node_functions.chains.tools.models.constants import CATEGORIZE_AGENT_REASON,UW_AGENT_REASON,PRODUCT_AGENT_REASON,PRODUCT_GROUNDING_REASON,LAST,UW_TOOL_NODE,PRODUCT_TOOL_NODE,BOTH
from app.node_functions.node_functions import uw_tool_node,product_tool_node

# -----------------------------
# Edge Router functions
# -----------------------------
def after_categorize_router(state: MedicareMessageGraph):
    category = state.get("agent_category")
    if category == "PRODUCT":
        return PRODUCT_AGENT_REASON
    elif category == "ELIGIBILITY_UNDERWRITING":
        return UW_AGENT_REASON
    elif category == "BOTH":
        return PRODUCT_AGENT_REASON
    else:
        return END

# def after_product_router_dep(state: MedicareMessageGraph):
#     category = state.get("agent_category")
#     if category == "PRODUCT":
#         return END
#     elif category == "BOTH":
#         return UW_AGENT_REASON
#     else:
#         return END

def after_product_router(state: MedicareMessageGraph) -> str:
    if not state["messages"][LAST].tool_calls:
    # if not isinstance(state["messages"][LAST], ToolMessage):
        category = state.get("agent_category")
        if category == "PRODUCT":
            return PRODUCT_GROUNDING_REASON
        elif category == "BOTH":
            return PRODUCT_GROUNDING_REASON
        else:
            return END
    return PRODUCT_TOOL_NODE
def after_grounded_router(state: MedicareMessageGraph) -> str:
    category = state.get("agent_category")
    if category == "PRODUCT":
        return END
    elif category == "BOTH":
        return UW_AGENT_REASON
    else:
        return END

def after_uw_router(state: MedicareMessageGraph) -> str:
    if not state["messages"][LAST].tool_calls:
        return END
    return UW_TOOL_NODE

medicare_graph = StateGraph(MedicareMessageGraph)

medicare_graph.add_node(CATEGORIZE_AGENT_REASON,categorize_agent_reason)
medicare_graph.add_node(UW_AGENT_REASON, uw_agent_reason)
medicare_graph.add_node(PRODUCT_AGENT_REASON,product_agent_reason)
medicare_graph.add_node(UW_TOOL_NODE, uw_tool_node)
medicare_graph.add_node(PRODUCT_TOOL_NODE, product_tool_node)
medicare_graph.add_node(PRODUCT_GROUNDING_REASON, product_grounding_reason)

medicare_graph.set_entry_point(CATEGORIZE_AGENT_REASON)

medicare_graph.add_conditional_edges(CATEGORIZE_AGENT_REASON, after_categorize_router, {
    END:END,
    PRODUCT_AGENT_REASON:PRODUCT_AGENT_REASON,
    UW_AGENT_REASON:UW_AGENT_REASON,
    BOTH:PRODUCT_AGENT_REASON})
medicare_graph.add_conditional_edges(PRODUCT_AGENT_REASON, after_product_router, {
    END:END,
    PRODUCT_GROUNDING_REASON:PRODUCT_GROUNDING_REASON,
    PRODUCT_TOOL_NODE:PRODUCT_TOOL_NODE})
medicare_graph.add_conditional_edges(UW_AGENT_REASON, after_uw_router, {
    END:END,
    UW_TOOL_NODE:UW_TOOL_NODE})
medicare_graph.add_edge(UW_TOOL_NODE, UW_AGENT_REASON)
medicare_graph.add_edge(PRODUCT_TOOL_NODE, PRODUCT_AGENT_REASON)
medicare_graph.add_conditional_edges(PRODUCT_GROUNDING_REASON,after_grounded_router, {
    END:END,
    UW_AGENT_REASON:UW_AGENT_REASON
})

medicare_graph = medicare_graph.compile()
medicare_graph.get_graph().draw_mermaid_png(output_file_path="medicare_flow_3.png")

# def run_graph(query: str) -> Dict[str, Any]:
def run_graph(query: str) -> MedicareMessageGraph:
    result = medicare_graph.invoke({"messages": [HumanMessage(
        content=query)]})
    # answer = result["messages"][LAST].content
    return result

if __name__ == "__main__":
    print("Hello from Medicare Agent")
    uw_query_1 = "a 67‑year‑old applicant who: Just left an employer group plan last month , Has several health conditions (COPD, diabetes, uses insulin) , Wants to enroll in Medigap Plan G , Has been on Medicare Part B for 18 months , Has no recent GI events except losing employer coverage , Has a hospitalization 45 days ago ,Uses oxygen at night. My question is - Does this client qualify for Guaranteed Issue because they just lost employer coverage, or do I need to submit them through full underwriting?"
    uw_query = "Evaluate the Medicare application. Its for state of Georgia, the start date of the medicare insurance is from 1st February 2026. Applicant is 65 years old, no prior coverage and no major health history"
    product_query_1 = "Explain Plan G"
    product_query_2 ="If I have Plan N, how much do I pay for an emergency room visit if I am admitted to the hospital?"
    combined_query="yet to add one"
    dummy_query = "hi"

    result = run_graph(uw_query_1)
    print("************************************************************************************ : Result")
    pprint(result)
    # pprint(result["answer"])