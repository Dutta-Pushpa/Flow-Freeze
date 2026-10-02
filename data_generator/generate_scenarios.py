"""Create labeled synthetic fraud scenarios for evaluation."""
import json
from pathlib import Path

def generate_scenarios():
    return {"scenarios": [{"incident_id": "INC001", "scenario_name": "Rapid Fund Diversion", "description": "Rapid distribution across downstream wallets before partial cash-out.", "reported_amount_bdt": 50000, "report_time": "2026-10-02 10:08:00", "source_wallet": "W001", "initial_recipient": "W002", "fraud_type": "suspected_account_takeover", "severity": "critical", "expected_downstream_wallets": ["W002", "W003", "W004", "W005", "W006", "W007"], "known_cashout_wallets": ["W003", "W004", "W007"], "ground_truth": {"predicted_next_wallet": "W007", "predicted_next_action": "cashout", "suspicious_value_bdt": 43000, "reachable_e_money_bdt": 26000, "recommended_intervention_amount_bdt": 26000}, "baseline": {"strategy": "direct_recipient_only", "wallet": "W002", "estimated_containable_value_bdt": 10000}}]}

if __name__ == "__main__":
    out = Path("data/synthetic/fraud_scenarios.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(generate_scenarios(), indent=2))
