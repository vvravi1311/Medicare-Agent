import streamlit as st
import pandas as pd
from pprint import pprint
from typing import Any, Dict, List
from app.medicare_agent_graph import run_graph
from langchain_core.messages import BaseMessage, HumanMessage
from app.node_functions.chains.tools.models.constants import (
    LANGCHAIN_TRACING,
    LANGCHAIN_PROJECT,
    LAST,
)
from dotenv import load_dotenv

load_dotenv()
from app.server_models import InvokeRequest
import os

st.set_page_config(page_title="Agent Underwriting Helper", layout="centered")
st.title("Agent Underwriting Helper")


def highlight_fired(row):
    color = "#ffe6e6" if row["outcome"] == "FIRED" else "white"
    return [f"background-color: {color}"] * len(row)


with st.sidebar:
    st.subheader("Session")
    if st.button("Clear chat", use_container_width=True):
        st.session_state.pop("messages", None)
        st.rerun()

# Adding an initial msg into the st session_state
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "user_query": "user_query in response ",
            "is_grounded": "true",
            "grounding_agent_answer": " grounding_agent_answer",
            "product_response_answer": "Ask me anything about Underwriting rules. I’ll check the UW rules and help you with analysis and cite the details on rules.",
            "product_audit": [
                {
                    "source": "02110-medigap-guide-health-insurance.pdf",
                    "page_number": 10,
                },
                {
                    "source": "02110-medigap-guide-health-insurance.pdf",
                    "page_number": 19,
                },
                {
                    "source": "02110-medigap-guide-health-insurance.pdf",
                    "page_number": 26,
                },
                {
                    "source": "02110-medigap-guide-health-insurance.pdf",
                    "page_number": 22,
                },
            ],
            "underwriting_response": " underwriting_response is here",
            "underwriting_audit": {
                "evaluatedAt": "2026-01-28T20:56:19.548508Z",
                "matchedRules": [
                    {
                        "ruleId": "R-600",
                        "outcome": "SKIPPED",
                        "details": "No continuous GI for GA",
                    },
                    {
                        "ruleId": "R-400",
                        "outcome": "FIRED",
                        "details": "Proceed to UW checks.",
                    },
                ],
            },
        }
    ]


# displaying the messages of the session_state in ui
def render_messages():
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg.get("user_query"):
                st.markdown("user_query : " + msg["user_query"])
            if msg.get("is_grounded"):
                st.markdown("is_grounded : " + str(msg["is_grounded"]))
            if msg.get("grounding_agent_answer"):
                st.markdown("grounding_agent_answer : " + msg["grounding_agent_answer"])
            if msg.get("underwriting_response"):
                st.markdown("underwriting_response : " + msg["underwriting_response"])
            if msg.get("underwriting_audit"):
                pprint(
                    "QQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQ"
                )
                pprint(msg.get("underwriting_audit"))
                pprint(
                    "QQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQQ"
                )

                st.markdown("underwriting_audit as following")
                audit = msg["underwriting_audit"]

                pprint(audit["matchedRules"])
                df = pd.DataFrame(audit["matchedRules"])
                st.dataframe(
                    df.style.apply(highlight_fired, axis=1), use_container_width=True
                )
            if msg.get("product_response_answer"):
                st.markdown(
                    "product_response_answer : " + msg["product_response_answer"]
                )
            if msg.get("product_audit"):
                st.markdown("product_audit as following")
                audit2 = msg["product_audit"]
                df2 = pd.DataFrame(audit2)
                st.dataframe(df2, use_container_width=True)


render_messages()
prompt = st.chat_input("Ask a question about Underwriting or Product...")
if prompt:
    st.session_state.messages.append({"role": "user", "user_query": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        try:
            with st.spinner("Retrieving docs and generating answer…"):
                InvokeRequest = InvokeRequest(query=prompt, thread_id="1234")
                result = run_graph(InvokeRequest)
                msg = {"role": "assistant"}

                # Grounding agent response
                ga = result.get("grounding_agent_response")
                if ga:
                    is_grounded = (
                        getattr(ga, "is_grounded", None) or ga.get("is_grounded")
                        if isinstance(ga, dict)
                        else None
                    )
                    grounding_answer = (
                        getattr(ga, "grounding_agent_answer", None)
                        or ga.get("grounding_agent_answer")
                        if isinstance(ga, dict)
                        else None
                    )

                    if is_grounded is not None:
                        msg["is_grounded"] = is_grounded
                    if grounding_answer:
                        msg["grounding_agent_answer"] = grounding_answer

                # Product response
                pr = result.get("product_response")
                if pr:
                    pr_answer = (
                        getattr(pr, "answer", None) or pr.get("answer")
                        if isinstance(pr, dict)
                        else None
                    )
                    pr_audit = (
                        getattr(pr, "audit", None) or pr.get("audit")
                        if isinstance(pr, dict)
                        else None
                    )

                    if pr_answer:
                        msg["product_response_answer"] = pr_answer
                    if pr_audit:
                        msg["product_audit"] = pr_audit

                # Underwriting response
                ur = result.get("underwriting_response")
                if ur:
                    ur_answer = (
                        getattr(ur, "answer", None) or ur.get("answer")
                        if isinstance(ur, dict)
                        else None
                    )
                    ur_audit = (
                        getattr(ur, "audit", None) or ur.get("audit")
                        if isinstance(ur, dict)
                        else None
                    )

                    if ur_answer:
                        msg["underwriting_response"] = ur_answer
                    if ur_audit:
                        msg["underwriting_audit"] = ur_audit[0]["audit_info"]

                # Append only the fields that exist
                st.session_state.messages.append(msg)
                render_messages()
        except Exception as e:
            st.error("Failed to generate a response.")
            st.exception(e)
