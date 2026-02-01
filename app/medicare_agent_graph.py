from typing import TypedDict, Annotated, Any, Dict
from pprint import pprint

from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage

from langgraph.graph import MessagesState, StateGraph,END

# project internal imports
from app.node_functions.node_functions import uw_agent_reason,MessageGraph
from app.node_functions.chains.tools.models.constants import UW_AGENT_REASON,LAST,UW_TOOL_NODE
from app.node_functions.node_functions import uw_tool_node



def should_continue(state: MessagesState) -> str:
    if not state["messages"][LAST].tool_calls:
        return END
    return UW_TOOL_NODE


medicare_graph = StateGraph(MessagesState)
medicare_graph.add_node(UW_AGENT_REASON, uw_agent_reason)
medicare_graph.add_node(UW_TOOL_NODE, uw_tool_node)
medicare_graph.set_entry_point(UW_AGENT_REASON)

medicare_graph.add_conditional_edges(UW_AGENT_REASON, should_continue, {
    END:END,
    UW_TOOL_NODE:UW_TOOL_NODE})
medicare_graph.add_edge(UW_TOOL_NODE, UW_AGENT_REASON)

medicare_graph = medicare_graph.compile()
medicare_graph.get_graph().draw_mermaid_png(output_file_path="medicare_flow.png")



# def run_graph(query: str) -> Dict[str, Any]:
def run_graph(query: str) -> MessageGraph:
    result = medicare_graph.invoke({"messages": [HumanMessage(
        content=query)]})
    answer = result["messages"][LAST].content
    return result

if __name__ == "__main__":
    print("Hello from Medicare Agent")
    query = "Evaluate the Medicare application. Its for state of Georgia, the start date of the medicare insurance is from 1st February 2026."
    result = run_graph(query)
    pprint(result)
    # pprint(result["answer"])