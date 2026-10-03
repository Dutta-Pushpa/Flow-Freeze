"""FastAPI model service: INPUT -> INTELLIGENCE -> ACTION -> OUTCOME -> FEEDBACK."""
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from backend.routes import incidents,transactions,graph,predictions,interventions
from backend.services.feedback_store import record_feedback
from fastapi import Depends
from backend.auth import require
from backend.security import security_demo
app=FastAPI(title="FlowFreeze Intelligence API",version="0.3.0",description="Traceable AI/ML services for MFS risk operations.")
app.include_router(incidents.router,prefix="/api/v1",dependencies=[Depends(require("score"))]); app.include_router(transactions.router,prefix="/api/v1",dependencies=[Depends(require("score"))]); app.include_router(graph.router,prefix="/api/v1",dependencies=[Depends(require("trace"))]); app.include_router(predictions.router,prefix="/api/v1",dependencies=[Depends(require("score"))]); app.include_router(interventions.router,prefix="/api/v1",dependencies=[Depends(require("recommend"))])
class Feedback(BaseModel):
    prediction: str = Field(min_length=1, max_length=80)
    analyst_decision: str = Field(min_length=1, max_length=80)
    actual_outcome: str = Field(min_length=1, max_length=80)
    feedback_id: str | None = None
    notes: str = Field(default="", max_length=1000)
@app.get("/health")
def health(): return {"ok":True,"service":"flowfreeze-intelligence","pipeline":["synthetic/public data","feature/context layer","trained ML models","explanation/recommendation","operator action","measurable outcome","feedback loop"],"model_stack":["HistGradientBoosting+isotonic calibration","Isolation Forest","exact Shapley attribution","scikit-learn","pandas"],"decision_boundary":"business policy remains outside free-form LLM"}
@app.get("/api/v1/evaluation",dependencies=[Depends(require("view"))])
def evaluation():
    from ml.training import evaluate_experiment
    return evaluate_experiment()
@app.get("/api/v1/security/demo",dependencies=[Depends(require("view"))])
def security(): return security_demo()
@app.post("/api/v1/feedback",dependencies=[Depends(require("feedback"))])
def feedback(payload: Feedback):
    try: return {"accepted":True,"stored":True,"feedback":record_feedback(payload.model_dump())}
    except ValueError as exc: raise HTTPException(status_code=422, detail=str(exc))
