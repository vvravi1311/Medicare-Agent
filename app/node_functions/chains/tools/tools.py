
from langchain_core.tools import tool

# project internal imports
from app.node_functions.chains.tools.models.uw_impl import evaluate
from app.node_functions.chains.tools.models.product_rag_impl import retrieve_product_context

# tools for the uw-agent
evaluate = tool(evaluate)
uw_tools =[evaluate]
# tools for the product rag-agent
retrieve_product_context=tool(retrieve_product_context)
product_rag_tools=[retrieve_product_context]

