"""Create labeled synthetic fraud scenarios for evaluation."""
import json
from pathlib import Path
def generate_scenarios():
    return [{"scenario_id":"fanout-001","label":"fraud","reported_amount":15000,"hops":3,"cashout":True},{"scenario_id":"near-miss-001","label":"legitimate","reported_amount":3200,"hops":1,"cashout":False}]
if __name__ == "__main__":
    out=Path("data/synthetic/scenarios.json"); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(generate_scenarios(),indent=2))
