const API_BASE = (import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000/api').replace(/\/$/, '')

export type Transaction = { id: string; customer_id: string; merchant_id: string; amount: number; location: string; payment_method: string; risk_score: number; status: string; device_id: string; created_at: string }
export type Incident = { id: string; title: string; severity: string; status: string; created_at: string }
export type Attack = { id: string; name: string; severity: string; status: string; accounts: number; devices: number; merchants: number; transactions: number; created_at: string }
export type DashboardData = { metrics: { transactions_monitored: number; active_threats: number; attacks_simulated: number; detection_rate: number; false_positive_rate: number; average_detection_time: number }; transactions: Transaction[]; incidents: Incident[] }
export type RiskAnalysis = { risk_score: number; classification: string; signals: Record<string, number | boolean>; reasons: string[]; recommended_action: string }
export type Investigation = { finding: string; evidence: string[]; risk: string; attack_type: string; recommended_action: string; risk_score: number; signals: Record<string, number | boolean>; analysis_mode: string }
export type Simulation = { id: string; status: string; stage: number; detection_score: number; created_at: string; attack_id?: string }

const fallbackTransactions: Transaction[] = [
 { id: 'TXN-84921', customer_id: 'C-A81F', merchant_id: 'M-M921', amount: 12840, location: 'Kolkata', payment_method: 'UPI', risk_score: 94, status: 'BLOCKED', device_id: 'D-X28', created_at: '2026-08-26T16:42:09Z' },
 { id: 'TXN-84920', customer_id: 'C-C44B', merchant_id: 'M-M104', amount: 2499, location: 'Mumbai', payment_method: 'Card', risk_score: 71, status: 'VERIFY', device_id: 'D-Q41', created_at: '2026-08-26T16:42:04Z' },
]
const fallback = { metrics: { transactions_monitored: 1284392, active_threats: 27, attacks_simulated: 8421, detection_rate: 94.8, false_positive_rate: 1.7, average_detection_time: 1.8 }, transactions: fallbackTransactions, incidents: [{ id: 'INC-204', title: 'Coordinated mule network', severity: 'CRITICAL', status: 'OPEN', created_at: '2026-08-26T16:38:00Z' }] }

async function request<T>(path: string, init?: RequestInit, fallbackValue?: T): Promise<T> {
 try { const response = await fetch(`${API_BASE}${path}`, { ...init, headers: { 'Content-Type': 'application/json', ...init?.headers } }); if (!response.ok) throw new Error(`API ${response.status}`); return await response.json() as T } catch (error) { console.warn(`EvoPay API unavailable for ${path}; using local demo data.`, error); if (fallbackValue !== undefined) return fallbackValue; throw error }
}
export type AnalyticsData = { detection_rate: number; false_positive_rate: number; average_response_time: number; daily_events: number[]; model_version?: string }
export type AuditEvent = { id: number; event_type: string; entity_id: string; details: string; created_at: string }
export type ModelVersion = { id: number; version: string; training_samples: number; precision: number; recall: number; f1: number; created_at: string }
export type ThreatPattern = { id: number; name: string; description: string; severity: string }

export const api = {
  dashboard: () => request<DashboardData>('/dashboard', undefined, fallback),
  transactions: (limit: number = 50, offset: number = 0) => request<Transaction[]>(`/transactions?limit=${limit}&offset=${offset}`, undefined, fallback.transactions),
  transaction: (id: string) => request<Transaction>(`/transactions/${id}`, undefined, fallback.transactions.find((item) => item.id === id) ?? fallback.transactions[0]),
  risk: (id: string) => request<RiskAnalysis>(`/transactions/${id}/risk`, undefined, { risk_score: 94, classification: 'CRITICAL', signals: { ml_score: 92, behavior_score: 88, anomaly_score: 95, graph_score: 97 }, reasons: ['High transaction velocity', 'Device linked to multiple accounts', 'Suspicious merchant relationship', 'Behavior differs significantly from historical baseline', 'Connected to high-risk network cluster'], recommended_action: 'BLOCK' }),
  analyze: (id: string) => request<RiskAnalysis>(`/transactions/${id}/analyze`, { method: 'POST' }, { risk_score: 94, classification: 'CRITICAL', signals: { ml_score: 92, behavior_score: 88, anomaly_score: 95, graph_score: 97 }, reasons: ['High transaction velocity', 'Device linked to multiple accounts'], recommended_action: 'BLOCK' }),
  action: (id: string, action: string) => request<{ transaction_id: string; status: string }>(`/transactions/${id}/action`, { method: 'POST', body: JSON.stringify({ action }) }, { transaction_id: id, status: action === 'ALLOW' ? 'ALLOWED' : action === 'BLOCK' ? 'BLOCKED' : action }),
  investigate: (id: string) => request<{ status: string; entity_id: string; notes?: string; investigation: Investigation }>('/investigate', { method: 'POST', body: JSON.stringify({ transaction_id: id }) }, { status: 'opened', entity_id: id, investigation: { finding: 'Transaction is likely part of a coordinated mule-network attack.', evidence: ['High transaction velocity', 'Device linked to multiple accounts', 'Suspicious network relationship'], risk: 'Critical', attack_type: 'Money mule network', recommended_action: 'BLOCK', risk_score: 94, signals: {}, analysis_mode: 'deterministic_local' } }),
  network: () => request<{ nodes: unknown[]; relationships: unknown[] }>('/network', undefined, { nodes: [], relationships: [] }),
  startSimulation: (attackId?: string) => request<Simulation>('/simulation/start', { method: 'POST', body: JSON.stringify({ attack_id: attackId }) }, { id: 'SIM-849201', status: 'RUNNING', stage: 1, detection_score: 85.8, created_at: new Date().toISOString() }),
  simulation: (id: string) => request<Simulation>(`/simulation/${id}`, undefined, { id, status: 'RUNNING', stage: 2, detection_score: 88.4, created_at: new Date().toISOString() }),
  adaptDefense: (pattern: string) => request<{ before_detection: number; after_detection: number; model_version: string; pattern?: string }>('/defense/adapt', { method: 'POST', body: JSON.stringify({ pattern }) }, { before_detection: 90.6, after_detection: 95.4, model_version: 'v1.1', pattern }),
  attacks: () => request<Attack[]>('/attacks', undefined, []),
  generateAttack: (attackType: string) => {
    const typeMap: Record<string, string> = { 'Synthetic Identity': 'synthetic_identity', 'Account Takeover': 'account_takeover', 'Card Testing': 'card_testing', 'Money Mule Network': 'money_mule', 'Merchant Collusion': 'merchant_collusion', 'Behavioral Mimicry': 'behavioral_mimicry', 'Device Rotation': 'device_rotation', 'Refund Abuse': 'refund_abuse', 'Velocity Attack': 'velocity_attack', 'Composite Attack': 'composite_attack' };
    return request<Attack>('/attacks/generate', { method: 'POST', body: JSON.stringify({ attack_type: typeMap[attackType] ?? 'composite_attack', strategy: attackType }) }, { id: 'EV-0421', name: attackType, severity: 'CRITICAL', status: 'UNDER SIMULATION', accounts: 18, devices: 7, merchants: 12, transactions: 2431, created_at: new Date().toISOString() });
  },
  evolveAttack: (attackId: string) => request<Attack>('/attacks/evolve', { method: 'POST', body: JSON.stringify({ attack_id: attackId }) }, { id: attackId, name: 'Synthetic Identity + Device Rotation + Mule Network', severity: 'CRITICAL', status: 'EVOLVED', accounts: 20, devices: 8, merchants: 12, transactions: 2431, created_at: new Date().toISOString() }),
  incidents: (limit: number = 50, offset: number = 0) => request<Incident[]>(`/incidents?limit=${limit}&offset=${offset}`, undefined, fallback.incidents),
  incidentAction: (id: string, status: string) => request<{ id: string; status: string }>(`/incidents/${id}/action`, { method: 'POST', body: JSON.stringify({ status }) }, { id, status }),
  analytics: () => request<AnalyticsData>('/analytics', undefined, { detection_rate: 94.8, false_positive_rate: 1.7, average_response_time: 1.8, daily_events: [42, 58, 49, 84, 72, 96, 88], model_version: 'v1.0' }),
  modelVersions: () => request<ModelVersion[]>('/model-versions', undefined, [{ id: 1, version: 'v1.0', training_samples: 80000, precision: 0.9945, recall: 0.9978, f1: 0.9962, created_at: '2026-08-26T16:00:00Z' }]),
  threatLibrary: () => request<ThreatPattern[]>('/threat-library', undefined, []),
  addThreatPattern: (name: string, description: string, severity: string = 'MEDIUM') => request<ThreatPattern>('/threat-library', { method: 'POST', body: JSON.stringify({ name, description, severity }) }),
  audit: (limit: number = 100) => request<AuditEvent[]>(`/audit?limit=${limit}`, undefined, []),
}
export { fallback as fallbackDashboard }
