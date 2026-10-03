import json, sys
from ml.training import evaluate_experiment, predict_next_move, predict_fraud, explain_fraud, impact_summary
from graph.simulator import simulate_flow

def main():
    command=sys.argv[1]; payload=json.loads(sys.stdin.read() or '{}')
    if command=='evaluation': result=evaluate_experiment()
    elif command=='fraud': result=predict_fraud(payload)
    elif command=='prediction': result=predict_next_move(payload)
    elif command=='explain': result=explain_fraud(payload)
    elif command=='impact': result=impact_summary()
    elif command=='simulation': result=simulate_flow(payload.get('edges',[]), payload.get('source','W4'), int(payload.get('delay_minutes',0)), float(payload.get('hold_ratio',68)), float(payload.get('initial_taint',15000)))
    else: raise SystemExit('unknown command')
    print(json.dumps(result))
if __name__=='__main__': main()
