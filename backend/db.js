import mysql from 'mysql2/promise';

let pool;
let status = { connected: false, mode: 'synthetic-fallback', message: 'DATABASE_URL not supplied; demo state is active.' };

const schema = `
CREATE TABLE IF NOT EXISTS flowfreeze_audit_events (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  actor VARCHAR(120) NOT NULL,
  action VARCHAR(160) NOT NULL,
  entity VARCHAR(120) NOT NULL,
  detail TEXT NOT NULL,
  reason TEXT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS flowfreeze_interventions (
  id VARCHAR(80) PRIMARY KEY,
  wallet_id VARCHAR(80) NOT NULL,
  decision VARCHAR(32) NOT NULL DEFAULT 'pending',
  amount DECIMAL(14,2) NOT NULL,
  reason TEXT NULL,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);`;

export async function initDatabase() {
  if (!process.env.DATABASE_URL) return status;
  try {
    pool = mysql.createPool(process.env.DATABASE_URL);
    for (const statement of schema.split(';').map((part) => part.trim()).filter(Boolean)) await pool.query(statement);
    status = { connected: true, mode: 'managed-mysql', message: 'Managed database connected.' };
  } catch (error) {
    status = { connected: false, mode: 'synthetic-fallback', message: `Database unavailable; using demo state (${error.message}).` };
  }
  return status;
}

export function databaseStatus() { return status; }

export async function saveDecision({ id, walletId, decision, amount, reason }) {
  if (!pool) return false;
  await pool.execute('INSERT INTO flowfreeze_interventions (id, wallet_id, decision, amount, reason) VALUES (?, ?, ?, ?, ?) ON DUPLICATE KEY UPDATE decision=VALUES(decision), amount=VALUES(amount), reason=VALUES(reason)', [id, walletId, decision, amount, reason]);
  await pool.execute('INSERT INTO flowfreeze_audit_events (actor, action, entity, detail, reason) VALUES (?, ?, ?, ?, ?)', ['Ayesha Rahman', `Intervention ${decision}`, id, `Wallet ${walletId} · ৳${Number(amount).toLocaleString('en-BD')}`, reason]);
  return true;
}
