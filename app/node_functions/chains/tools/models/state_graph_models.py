
from typing import TypedDict, Annotated, Any, Dict, Optional,List
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

# class MessageGraph(TypedDict):
#     messages: Annotated[list[BaseMessage], add_messages]

class Audit(BaseModel):
    source:Optional[str]
    page_number:Optional[str]
    audit_info: Dict[str, Any]
class ProductAgentResponse(BaseModel):
    answer: Optional[str] = ""
    audit: Optional[List[Audit]] = Field(default_factory=list)
class AnyAgentResponse(BaseModel):
    answer: Optional[str] = ""
    audit: Optional[List[Audit]] = Field(default_factory=list)
class GroundingAgentResponse(BaseModel):
    is_grounded:Optional[bool]  = Field(default="", description="Whether the answer is grounded in retrieved evidence.")
    grounding_agent_answer:Optional[str] = Field(default="", description="The final natural-language answer")
class MedicareMessageGraph(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    uw_agent_messages: Annotated[list[BaseMessage], add_messages]
    # Input from the user
    user_query: Optional[str]
    error_message: Optional[str]
    # Output from the categorizer
    agent_category: Optional[str]
    # Output from the product agent
    product_response: Optional[ProductAgentResponse]
    grounding_agent_response: Optional[GroundingAgentResponse]
    # Output from the eligibility/underwriting agent
    underwriting_response: Optional[AnyAgentResponse]
