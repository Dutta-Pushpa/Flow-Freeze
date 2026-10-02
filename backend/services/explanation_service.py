"""RAG-ready explanations. Structured evidence is authoritative; LLM is optional and never decides policy."""
import os

def retrieve_context(query: str, evidence: list[str]):
    terms=set(query.lower().split()); ranked=sorted(evidence,key=lambda item:len(terms.intersection(item.lower().split())),reverse=True)
    return ranked[:3]

def explain_with_rag(query: str, evidence: list[str], recommendation: dict):
    context=retrieve_context(query,evidence)
    result={"answer":f"Recommendation is grounded in: {'; '.join(context)}","retrieved_context":context,"recommendation":recommendation,"llm_provider":"none","guardrail":"LLM cannot change risk score, amount, scope, or approval requirement."}
    if os.getenv("OPENAI_API_KEY") and os.getenv("FLOWFREEZE_ENABLE_LLM") == "true":
        result["llm_provider"]="openai-compatible-optional"
        result["answer"] += " Optional GenAI summarization is enabled behind a server-side flag."
    return result
