from langchain_aws import ChatBedrock
from langchain_core.prompts import ChatPromptTemplate
from app.node_functions.chains.tools.models.state_graph_models import JudgeAgentResponse

judge_prompt_str = """
You will be given a context and a question.
Your task is to evaluate the question based on the given context and provide a score between 1 and 5.

Use the following rules to make the evaluation:
- Read the context and question carefully.
- Analyse and evaluate the question based on the provided evaluation criteria.
- Provide a scaled score between 1 and 5 that reflects your evaluation.

Provide a score between 1 and 5 based on the following criteria:
- Score 1: The context does not provide sufficient information to answer the question in any way.
- Score 2 or 3: The context provides some relevant information, but the question remains partially answerable or is unclear/ambiguous.
- Score 4: The context offers sufficient information to answer the question, but some minor details are missing or unclear.
- Score 5: The context provides all necessary information to answer the question clearly and without ambiguity.

Now here is the context (delimited by triple quotes):

Context: \"\"\"{context}\"\"\" \n

Now here is the question (delimited by triple quotes):

Context: \"\"\"{question}\"\"\" \n

Please use the JSON schema below for your output:

Generate the output in the following JSON format consisting of one dictionary with two elements:
Output format (JSON):
    {{
      "evaluation": your rationale for the rating, as a text,
      "score": "your rating, as a number between 1 and 5"
    }}
Return the output in the required JSON format only.
"""


def create_judge_llm(model_id="amazon.nova-pro-v1:0", region="us-east-1"):
    return ChatBedrock(model_id=model_id, region_name=region)


judge_llm = create_judge_llm().with_structured_output(
    JudgeAgentResponse
)  # <-- instantiate here

judge_prompt = ChatPromptTemplate.from_messages(
    [
        (judge_prompt_str),
    ]
)

judge_chain = (
    {"question": lambda x: x["question"], "context": lambda x: x["context"]}
    | judge_prompt
    | judge_llm
)
