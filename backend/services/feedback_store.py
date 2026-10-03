from __future__ import annotations
import hashlib, json, os
from datetime import datetime, timezone
from pathlib import Path

PATH = Path(os.getenv("FLOWFREEZE_FEEDBACK_PATH", "data/feedback/feedback.jsonl"))

def record_feedback(payload: dict) -> dict:
    required = ["prediction", "analyst_decision", "actual_outcome"]
    missing = [key for key in required if payload.get(key) in (None, "")]
    if missing: raise ValueError("Missing required feedback fields: " + ", ".join(missing))
    prediction = str(payload["prediction"]).lower(); actual = str(payload["actual_outcome"]).lower(); decision = str(payload["analyst_decision"])
    correctness = prediction == actual
    previous = "GENESIS"
    if PATH.exists():
        last = PATH.read_text().strip().splitlines()
        if last: previous = json.loads(last[-1])["event_hash"]
    event = {"feedback_id": payload.get("feedback_id", datetime.now(timezone.utc).strftime("fb-%Y%m%d%H%M%S%f")), "prediction": prediction, "analyst_decision": decision, "actual_outcome": actual, "correct": correctness, "notes": payload.get("notes", ""), "recorded_at": datetime.now(timezone.utc).isoformat(), "previous_hash": previous}
    event["event_hash"] = hashlib.sha256(json.dumps(event, sort_keys=True).encode()).hexdigest()
    PATH.parent.mkdir(parents=True, exist_ok=True); with_open = PATH.open("a", encoding="utf-8")
    with with_open as handle: handle.write(json.dumps(event, sort_keys=True) + "\n")
    return event

def verify_audit_integrity() -> dict:
    previous = "GENESIS"; checked = 0
    if not PATH.exists(): return {"ok": True, "checked": 0}
    for line in PATH.read_text().splitlines():
        event = json.loads(line); expected = event.pop("event_hash"); valid = event.get("previous_hash") == previous and hashlib.sha256(json.dumps(event, sort_keys=True).encode()).hexdigest() == expected
        if not valid: return {"ok": False, "checked": checked, "failed_feedback_id": event.get("feedback_id")}
        previous = expected; checked += 1
    return {"ok": True, "checked": checked, "last_hash": previous}
