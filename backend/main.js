import express from 'express';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { cloneStore, createDemoState } from './services/demo-data.js';
import { databaseStatus, initDatabase, saveDecision } from './db.js';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, '..');
const app = express();
const port = Number(process.env.PORT || 3000);
const demo = createDemoState();

app.get('/_app/health', (req, res) => res.json({ ok: true, service: 'flowfreeze', mode: 'synthetic-demo', database: databaseStatus() }));
app.get('/api/health', (req, res) => res.json({ ok: true, database: databaseStatus() }));
app.get('/manus-routes.json', (req, res) => res.sendFile(path.join(root, 'frontend', 'public', 'manus-routes.json')));
app.get('/api/bootstrap', (req, res) => res.json(cloneStore(demo)));
app.get('/api/overview', (req, res) => res.json(demo.overview));
app.get('/api/incidents', (req, res) => res.json(demo.incidents));
app.get('/api/incidents/:id', (req, res) => { const incident = req.params.id === demo.incident.id ? demo.incident : demo.incidents.find((item) => item.id === req.params.id); incident ? res.json(incident) : res.status(404).json({ error: 'Incident not found' }); });
app.get('/api/transactions', (req, res) => res.json(demo.transactions));
app.get('/api/graph', (req, res) => res.json(demo.graph));
app.get('/api/wallets/:id', (req, res) => { const wallet = demo.wallets.find((item) => item.id === req.params.id); wallet ? res.json(wallet) : res.status(404).json({ error: 'Wallet not found' }); });
app.get('/api/predictions/:walletId', (req, res) => res.json({ wallet: req.params.walletId, forward: 0.12, cashout: 0.81, other: 0.07, horizonMinutes: 5, explanation: 'Cash-out probability is elevated by rapid forwarding and agent-like downstream behavior.' }));
app.get('/api/interventions', (req, res) => res.json(demo.intervention));
app.get('/api/interventions/:id', (req, res) => res.json(demo.intervention));
app.post('/api/interventions/:id/decision', async (req, res) => { const { decision, reason, amount } = req.body || {}; if (!['approved', 'rejected', 'modified'].includes(decision) || !String(reason || '').trim()) return res.status(400).json({ error: 'decision and reason are required' }); demo.intervention.decision = decision; demo.intervention.reason = reason; demo.intervention.amount = Math.max(0, Math.min(Number(amount || demo.intervention.tainted), demo.intervention.balance)); demo.audit.unshift({ time: 'Just now', actor: 'Ayesha Rahman', action: `Intervention ${decision}`, entity: demo.intervention.id, detail: `${demo.intervention.scope} · ৳${demo.intervention.amount.toLocaleString('en-BD')}`, tone: decision === 'approved' ? 'mint' : 'coral' }); await saveDecision({ id: demo.intervention.id, walletId: demo.intervention.wallet, decision, amount: demo.intervention.amount, reason }).catch(() => false); res.json({ ok: true, intervention: demo.intervention, audit: demo.audit[0] }); });
app.get('/api/simulator', (req, res) => { const delay = Math.max(0, Number(req.query.delay || 0)); const hold = Math.max(25, Math.min(100, Number(req.query.hold || 68))); const preserved = Math.max(0, Math.round(193800 - delay * 4800 - Math.abs(hold - 68) * 80)); const collateral = Math.max(0, Math.round((100 - hold) * 100)); const cashout = Math.min(99, Math.round(68 + delay * 4)); const innocence = Math.max(0, Math.round((100 - hold) * 70)); res.json({ delay, hold, preserved, collateral, cashout, innocence }); });
app.get('/api/evaluation', (req, res) => res.json(demo.evaluation));
app.get('/api/audit', (req, res) => res.json(demo.audit));

app.get('/api/intelligence/health', async (req, res) => {
  const base = process.env.PYTHON_API_URL || 'http://127.0.0.1:8000';
  try { const response = await fetch(`${base}/health`); return res.status(response.status).json(await response.json()); }
  catch (error) { return res.json({ ok: true, service: 'flowfreeze-intelligence', mode: 'node-fallback', python_api: base, error: error.message, pipeline: ['synthetic/public data','feature & context layer','ML/AI engine','explanation / recommendation','operator action','measurable outcome','feedback loop'] }); }
});
app.post('/api/intelligence/recommend', async (req, res) => {
  const base = process.env.PYTHON_API_URL || 'http://127.0.0.1:8000';
  try { const response = await fetch(`${base}/api/v1/interventions/recommend`, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(req.body) }); return res.status(response.status).json(await response.json()); }
  catch (error) { const body = req.body || {}; const amount = Number(body.reported_amount || 15000); const balance = Number(body.wallet_balance || 22000); return res.json({ recommendation: { amount, scope: 'wallet-level partial hold', rationale: 'Fallback recommendation grounded in reported flow continuity and cash-out likelihood.', confidence: .83, collateral_estimate: Math.max(0, balance - amount), requires_human_approval: true, trace_id: 'node-fallback-001' }, grounding: { retrieved_context: body.evidence || [], llm_provider: 'none', guardrail: 'LLM cannot change risk score, amount, scope, or approval requirement.', error: error.message } }); }
});

app.use(express.static(path.join(root, 'dist')));
app.use('/frontend', express.static(path.join(root, 'frontend')));
app.use('/public', express.static(path.join(root, 'public')));
app.get('*', (req, res) => { if (req.path.startsWith('/api/')) return res.status(404).json({ error: 'API route not found' }); res.sendFile(path.join(root, 'dist', 'index.html'), (error) => { if (error) res.sendFile(path.join(root, 'index.html')); }); });

initDatabase().then(() => app.listen(port, '0.0.0.0', () => console.log(`FlowFreeze listening on 0.0.0.0:${port}`))).catch((error) => { console.error(error); process.exit(1); });
