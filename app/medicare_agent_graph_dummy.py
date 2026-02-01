from typing import TypedDict, Annotated, Any, Dict
from pprint import pprint


from langchain_core.messages import BaseMessage, AIMessage, HumanMessage

from langgraph.graph import MessagesState, StateGraph, END
from langgraph.graph.message import add_messages

# project internal imports
from app.node_functions.chains.tools.models.constants import PLANNER_AGENT
from .server_models import InvokeRequest

# -----------------------------------imports complete -----------------------------


# Define the State
class MessageGraph(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

def planner_agent(state: MessageGraph):
    return {"messages": [AIMessage(content="this is a mock response form an agent. to test if API is hosted successfully in aws")]}

# define the graph flow
flow = StateGraph(MessagesState)
flow.add_node(PLANNER_AGENT, planner_agent)
flow.set_entry_point(PLANNER_AGENT)
flow.add_edge(PLANNER_AGENT,END)

# compile the graph
uw_flow = flow.compile()
uw_flow.get_graph().draw_mermaid_png(output_file_path="uw_flow.png")

# function to invoke the graph and transform the response
def run_medicare_agent(InvokeRequest : InvokeRequest) -> Dict[str, Any]:
    result = uw_flow.invoke({"messages": [HumanMessage(
        content= " my query")]}) #, config=InvokeRequest["config"])
    return result["messages"]

if __name__ == "__main__":
    print("Hello from Medicare agent")
    query = "hello from the user"
    res = run_medicare_agent({"query": query, "thread_id": "INC1234"})
    pprint(res)

