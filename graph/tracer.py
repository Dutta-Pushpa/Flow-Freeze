from collections import defaultdict,deque
def trace_flow(edges, source, max_hops=5):
    adj=defaultdict(list)
    for edge in edges: adj[edge["sender_wallet"]].append(edge)
    seen={source}; queue=deque([(source,0)]); result=[]
    while queue:
        node,hop=queue.popleft()
        if hop>=max_hops: continue
        for edge in adj[node]:
            result.append({**edge,"hop":hop+1}); target=edge["receiver_wallet"]
            if target not in seen: seen.add(target); queue.append((target,hop+1))
    return result
