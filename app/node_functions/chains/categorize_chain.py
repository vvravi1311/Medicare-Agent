from dotenv import load_dotenv

load_dotenv()

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# project internal imports
from app.node_functions.chains.tools.models.constants import CATEGORIZE_AGENT_MODEL

prompt_str = """
You are a classification agent. Your job is to categorize the agents Medicare Supplement insurance related queries into exactly one of the four categories:

1. PRODUCT  
2. ELIGIBILITY_UNDERWRITING  
3. GENERAL

Rules:
- respond with PRODUCT when questions are about product features, product benefits, product coverage, product pricing or product details.
- respond with ELIGIBILITY_UNDERWRITING when questions are about risk, qualification, underwriting rules or approval criteria.
- For all other type of queries respond with GENERAL

Respond only one of the words: PRODUCT, ELIGIBILITY_UNDERWRITING, GENERAL.

Example:
 - “What does Plan G cover compared to Plan N?” → PRODUCT
 - “How much is the premium for Plan F in California?” → PRODUCT
 - “What are the differences between High‑Deductible Plan G and regular Plan G?” → PRODUCT
 - “Will my COPD cause a decline for Plan G?” → ELIGIBILITY_UNDERWRITING
 - “Can I switch Medigap plans without medical underwriting in my state?” → ELIGIBILITY_UNDERWRITING
 - “What is the difference between Medicare Advantage and Medicare Supplement?” → GENERAL
 - “How do I find my Medicare number?” → GENERAL


"""
categorize_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", prompt_str),
        MessagesPlaceholder(variable_name="categorize_messages"),
    ]
)

categorize_llm = ChatOpenAI(model=CATEGORIZE_AGENT_MODEL, temperature=0)
categorize_chain = categorize_prompt | categorize_llm
