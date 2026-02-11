
from typing import TypedDict, Annotated, Any, Dict, Optional,List
from pydantic import BaseModel, Field
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

# class MessageGraph(TypedDict):
#     messages: Annotated[list[BaseMessage], add_messages]
class judge_info(BaseModel):
    source:Optional[str]
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
class JudgeAgentResponse(BaseModel):
    evaluation:Optional[str]  = Field(default="", description="rationale for the rating, as a text")
    score:Optional[int] = Field(default="", description="rating, as a number between 1 and 5")
class MedicareMessageGraph(TypedDict):
    # State messages used
    messages: Annotated[list[BaseMessage], add_messages]
    # Graph state of the individual agent reasons
    uw_agent_messages: Annotated[list[BaseMessage], add_messages]
    product_response: Optional[ProductAgentResponse]
    grounding_agent_response: Optional[GroundingAgentResponse]
    underwriting_response: Optional[AnyAgentResponse]
    # Input from the user
    user_query: Optional[str]
    agent_category: Optional[str]
    final_answer: Optional[str]
    audit: Optional[List[Audit]] = Field(default_factory=list)
    judge_evaluation_score : Optional[str]
    # error_message: Optional[str]

