"""FastAPI model service: INPUT -> INTELLIGENCE -> ACTION -> OUTCOME -> FEEDBACK."""
from fastapi import FastAPI
from pydantic import BaseModel
from backend.routes import incidents,transactions,graph,predictions,interventions
app=FastAPI(title="FlowFreeze Intelligence API",version="0.2.0",description="Traceable AI/ML services for MFS risk operations.")
app.include_router(incidents.router,prefix="/api/v1"); app.include_router(transactions.router,prefix="/api/v1"); app.include_router(graph.router,prefix="/api/v1"); app.include_router(predictions.router,prefix="/api/v1"); app.include_router(interventions.router,prefix="/api/v1")
class Feedback(BaseModel):
    entity_id: str
    outcome: str
    analyst_label: str|None=None
    notes: str|None=None
@app.get("/health")
def health(): return {"ok":True,"service":"flowfreeze-intelligence","pipeline":["synthetic/public data","feature/context layer","ML/AI engine","explanation/recommendation","operator action","measurable outcome","feedback loop"],"model_stack":["pandas","scikit-learn","XGBoost/LightGBM adapters","PyTorch-ready","optional OpenAI-compatible LLM/RAG"],"decision_boundary":"business policy remains outside free-form LLM"}
@app.post("/api/v1/feedback")
def feedback(payload: Feedback): return {"accepted":True,"stored":False,"message":"Feedback is validated; configure PostgreSQL persistence to store it.","feedback":payload.model_dump()}
