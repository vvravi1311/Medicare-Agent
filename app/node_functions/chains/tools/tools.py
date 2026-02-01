
from langchain_core.tools import tool

# project internal imports
from app.node_functions.chains.tools.models.uw_impl import evaluate

# tools for the uw-agent
evaluate = tool(evaluate)
uw_tools =[evaluate]

# tools for the product rag-agent