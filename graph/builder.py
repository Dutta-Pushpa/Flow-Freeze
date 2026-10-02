import pandas as pd
def build_graph(transactions: pd.DataFrame):
    nodes=set(transactions["sender_wallet"]).union(transactions["receiver_wallet"]); edges=transactions[["sender_wallet","receiver_wallet","amount","timestamp"]].to_dict("records"); return {"nodes":[{"id":n} for n in sorted(nodes)],"edges":edges}
