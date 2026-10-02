"""RAG-ready explanations. Structured evidence is authoritative; LLM is optional and never decides policy."""
import os

def retrieve_context(query: str, evidence: list[str]):
    terms=set(query.lower().split()); ranked=sorted(evidence,key=lambda item:len(terms.intersection(item.lower().split())),reverse=True)
    return ranked[:3]

def explain_with_rag(query: str, evidence: list[str], recommendation: dict):
    context=retrieve_context(query,evidence)
    result={"answer":f"Recommendation is grounded in: {'; '.join(context)}","retrieved_context":context,"recommendation":recommendation,"llm_provider":"none","guardrail":"LLM cannot change risk score, amount, scope, or approval requirement."}
    if os.getenv("OPENAI_API_KEY") and os.getenv("FLOWFREEZE_ENABLE_LLM") == "true":
        try:
            from openai import OpenAI
            client=OpenAI()
            prompt=("Summarize the retrieved evidence for an authorized MFS risk analyst in two concise sentences. "
                    "Do not decide, change, or endorse an intervention. State that the recommendation remains human-gated.\n"
                    f"Incident query: {query}\nRetrieved evidence: {context}\nStructured recommendation: {recommendation}")
            response=client.chat.completions.create(
                model=os.getenv("FLOWFREEZE_LLM_MODEL","gpt-5-mini"),
                messages=[
                    {"role":"system","content":"You are a grounded explanation assistant. Evidence and structured policy are authoritative."},
                    {"role":"user","content":prompt},
                ],
                max_completion_tokens=220,
                extra_body={"reasoning":{"effort":"minimal"}},
            )
            result["answer"]=response.choices[0].message.content or result["answer"]
            result["llm_provider"]="openai-compatible"
            result["model"]=os.getenv("FLOWFREEZE_LLM_MODEL","gpt-5-mini")
        except Exception as error:
            result["llm_provider"]="openai-compatible-fallback"
            result["llm_error"]=str(error)
    return result
