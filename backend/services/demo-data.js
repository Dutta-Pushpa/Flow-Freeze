const now = new Date('2026-10-02T10:44:12+06:00');
const minutesAgo = (minutes) => new Date(now.getTime() - minutes * 60_000).toISOString();

export const products = [
  { id: 'demo-ledger', title: 'FlowFreeze field notebook', price: 650, description: 'A compact notebook for evidence-first investigations.', image: 'https://images.unsplash.com/photo-1544816155-12df9643f363?auto=format&fit=crop&w=800&q=80' },
  { id: 'demo-kit', title: 'Analyst desk kit', price: 1450, description: 'Cards, tabs and markers for incident-room reviews.', image: 'https://images.unsplash.com/photo-1517842645767-c639042777db?auto=format&fit=crop&w=800&q=80' }
];

export function createDemoState() {
  const transactions = [
    { id: 'TX-77A21', timestamp: minutesAgo(6), sender: 'VICTIM-01', receiver: 'W1', amount: 15000, type: 'wallet_transfer', channel: 'USSD', agent: 'AG-204', location: 'Dhaka', senderBalanceBefore: 42000, senderBalanceAfter: 27000, receiverBalanceBefore: 0, receiverBalanceAfter: 15000 },
    { id: 'TX-77A22', timestamp: minutesAgo(4), sender: 'W1', receiver: 'W4', amount: 15000, type: 'wallet_transfer', channel: 'App', agent: 'AG-204', location: 'Dhaka', senderBalanceBefore: 15000, senderBalanceAfter: 0, receiverBalanceBefore: 7000, receiverBalanceAfter: 22000 },
    { id: 'TX-77A23', timestamp: minutesAgo(3), sender: 'W4', receiver: 'W2', amount: 7000, type: 'wallet_transfer', channel: 'App', agent: 'AG-204', location: 'Dhaka', senderBalanceBefore: 22000, senderBalanceAfter: 15000, receiverBalanceBefore: 1200, receiverBalanceAfter: 8200 },
    { id: 'TX-77A24', timestamp: minutesAgo(2), sender: 'W4', receiver: 'AG-07', amount: 8000, type: 'cash_out', channel: 'Agent', agent: 'AG-07', location: 'Mirpur', senderBalanceBefore: 22000, senderBalanceAfter: 14000, receiverBalanceBefore: 41000, receiverBalanceAfter: 49000 },
    { id: 'TX-77A25', timestamp: minutesAgo(1), sender: 'AG-07', receiver: 'CASH', amount: 8000, type: 'cash_out', channel: 'Agent', agent: 'AG-07', location: 'Mirpur', senderBalanceBefore: 49000, senderBalanceAfter: 41000, receiverBalanceBefore: 0, receiverBalanceAfter: 0 },
    { id: 'TX-76F11', timestamp: minutesAgo(48), sender: 'VICTIM-02', receiver: 'W2', amount: 8200, type: 'wallet_transfer', channel: 'App', agent: 'AG-111', location: 'Uttara', senderBalanceBefore: 15000, senderBalanceAfter: 6800, receiverBalanceBefore: 0, receiverBalanceAfter: 8200 }
  ];
  const wallets = [
    { id: 'W1', balance: 0, accountAge: '4 days', customerType: 'Personal', averageTransactionAmount: 12000, frequency: '6.2 tx / hr', normalActiveHours: '18:00 — 22:00', behavior: 'Rapid relay', riskFactors: ['New account', 'Full-balance forwarding'], taint: 0 },
    { id: 'W2', balance: 8200, accountAge: '12 days', customerType: 'Personal', averageTransactionAmount: 3800, frequency: '3.8 tx / hr', normalActiveHours: '09:00 — 18:00', behavior: 'Layering candidate', riskFactors: ['New recipient relationship', 'Multiple inbound sources'], taint: 8200 },
    { id: 'W4', balance: 22000, accountAge: '19 days', customerType: 'Personal', averageTransactionAmount: 2600, frequency: '9.4 tx / hr', normalActiveHours: '18:00 — 22:00', behavior: 'High-velocity pass-through', incoming: 15000, outgoing: 15000, taint: 15000, ratio: 0.68, riskFactors: ['New recipient relationship', 'Rapid forwarding after receipt', 'Agent-like cash-out path'], related: ['INC-2407', 'INC-2398'] },
    { id: 'W7', balance: 12400, accountAge: '4 years', customerType: 'Personal', averageTransactionAmount: 3400, frequency: '1.4 tx / hr', normalActiveHours: '08:00 — 20:00', behavior: 'Stable consumer', riskFactors: ['Unusual recipient', 'Normal account age'], taint: 0 }
  ];
  const incidents = [
    { id: 'INC-2407', title: 'Rapid fan-out after disputed transfer', type: 'suspected fraud', status: 'Needs review', risk: 92, amount: 15000, wallet: 'W4', reportedAt: 'Today, 10:42', confidence: 0.81, nextMove: 'Cash-out' },
    { id: 'INC-2404', title: 'Multi-hop layering across new wallets', type: 'suspected fraud', status: 'Investigating', risk: 84, amount: 8200, wallet: 'W2', reportedAt: 'Today, 09:17', confidence: 0.74, nextMove: 'Forward' },
    { id: 'INC-2399', title: 'Wrong-recipient dispute', type: 'customer dispute', status: 'Needs context', risk: 38, amount: 3200, wallet: 'W7', reportedAt: 'Yesterday, 18:22', confidence: 0.67, nextMove: 'No movement' }
  ];
  const incident = { ...incidents[0], tainted: 15000, balance: 22000, nextMove: { forward: 0.12, cashout: 0.81, other: 0.07 }, evidence: ['W4 received ৳15,000 from a fraud-linked wallet within 2 minutes of the report.', 'W4 forwarded ৳8,000 to an agent-like wallet and retains ৳22,000 digital balance.', 'The proportional taint estimate isolates the reported value instead of the full wallet balance.'], timeline: [{ time: '10:38', label: 'Reported transfer', detail: 'Victim → W1 · ৳15,000' }, { time: '10:40', label: 'Layer 1 detected', detail: 'W1 → W4 · ৳15,000' }, { time: '10:42', label: 'Incident created', detail: 'Risk engine scored flow at 92/100' }, { time: '10:44', label: 'Recommendation ready', detail: 'Partial hold candidate · ৳15,000' }] };
  return {
    overview: { activeIncidents: 3, suspiciousFlows: 12, valueAtRisk: 286400, valuePreserved: 193800, preservedChange: 18.4, riskChange: -7.2 },
    incidents, incident, transactions, wallets,
    graph: { nodes: [{ id: 'VICTIM-01', label: 'Victim', x: 90, y: 155, kind: 'victim', balance: 0 }, { id: 'W1', label: 'W1', x: 255, y: 80, kind: 'wallet', balance: 15000 }, { id: 'W4', label: 'W4', x: 430, y: 155, kind: 'wallet risk', balance: 22000 }, { id: 'W2', label: 'W2', x: 600, y: 80, kind: 'wallet', balance: 8200 }, { id: 'AG-07', label: 'Agent 7', x: 600, y: 230, kind: 'cashout', balance: 8000 }, { id: 'CASH', label: 'Cash-out', x: 790, y: 230, kind: 'cashout', balance: 8000 }], links: [{ from: 'VICTIM-01', to: 'W1', amount: 15000, time: '10:38' }, { from: 'W1', to: 'W4', amount: 15000, time: '10:40' }, { from: 'W4', to: 'W2', amount: 7000, time: '10:41' }, { from: 'W4', to: 'AG-07', amount: 8000, time: '10:42' }, { from: 'AG-07', to: 'CASH', amount: 8000, time: '10:43' }] },
    wallet: wallets.find((wallet) => wallet.id === 'W4'),
    intervention: { id: 'INT-1001', wallet: 'W4', risk: 92, tainted: 15000, balance: 22000, cashout: 81, confidence: 81, collateral: 7000, scope: 'Wallet-level partial hold', rationale: 'Most evidence links ৳15,000 to the reported incident. A full freeze would expose an estimated ৳7,000 of legitimate value.', evidence: ['Direct receipt from W1', 'Cash-out probability above 80%', 'Taint amount is below current balance'], decision: 'pending' },
    evaluation: { baseline: { precision: 0.61, recall: 0.54, f1: 0.57, preserved: 108400, collateral: 46200 }, flowfreeze: { precision: 0.84, recall: 0.79, f1: 0.81, preserved: 193800, collateral: 12800 } },
    audit: [{ time: 'Today, 10:44', actor: 'Risk engine', action: 'Recommendation generated', entity: 'INT-1001', detail: 'Partial hold · W4 · ৳15,000', tone: 'indigo' }, { time: 'Today, 10:42', actor: 'Ayesha Rahman', action: 'Incident created', entity: 'INC-2407', detail: 'Risk score 92 · suspected fraud', tone: 'coral' }, { time: 'Today, 10:40', actor: 'FlowFreeze', action: 'Flow traced', entity: 'TX-77A21', detail: '2 hops · cash-out point found', tone: 'mint' }, { time: 'Today, 10:38', actor: 'System import', action: 'Transaction received', entity: 'TX-77A21', detail: 'Victim → W1 · ৳15,000', tone: 'slate' }],
    storefront: { connected: Boolean(process.env.SHOPIFY_STORE_DOMAIN && process.env.SHOPIFY_STOREFRONT_ACCESS_TOKEN), products, cart: { lines: [], total: 0 } }
  };
}

export function cloneStore(store) { return JSON.parse(JSON.stringify(store)); }
