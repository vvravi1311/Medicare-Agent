from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
load_dotenv()
from app.node_functions.chains.tools.tools import uw_tools

# project internal imports
from app.node_functions.chains.tools.models.constants import UW_AGENT_MODEL
prompt_str = (
    "You are a Medicare Supplement underwriting assistant for internal agents. "
    "Use tools to answer the questions; do not create new underwriting rules. "
    "Do not create placeholder values, defaults, or synthetic data. "
    "Do not proceed with a tool call until the user supplies all required data. "
    "If the user’s request is incomplete, ask clarifying questions. "
    "If the user provides all required fields, proceed with the tool call. "
    "If the user provides contradictory or ambiguous data, ask for clarification. "
    "Explain whether the situation sounds like Open Enrollment, Guaranteed Issue, or Underwritten, "
    "along with any key considerations or typical knock-out conditions. "
    "If more details such as dates, prior coverage, or health history are needed, explicitly say so. "
    "Do not promise approval; instead say 'typically' or 'subject to underwriting review.'"
)

uw_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            prompt_str
        ),
        MessagesPlaceholder(variable_name="uw_messages"),
    ]
)

uw_llm = ChatOpenAI(model=UW_AGENT_MODEL, temperature=0).bind_tools(uw_tools)
# uw_llm = ChatOpenAI(model=UW_AGENT_MODEL, temperature=0, api_key=os.environ.get("OPENAI_API_KEY")).bind_tools(uw_tools)
uw_chain = uw_prompt | uw_llm