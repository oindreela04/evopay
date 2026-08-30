const API_BASE = (import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000/api').replace(/\/$/, '')

export class ApiError extends Error {
  readonly status: number | null
  readonly path: string
  readonly cause?: unknown
  constructor(message: string, path: string, status: number | null = null, cause?: unknown) { super(message); this.name = 'ApiError'; this.path = path; this.status = status; this.cause = cause }
}

export type Transaction = { id: string; customer_id: string; merchant_id: string; amount: number; location: string; payment_method: string; risk_score: number; status: string; device_id: string; created_at: string; synthetic: boolean }
export type Incident = { id: string; title: string; severity: string; status: string; created_at: string; transaction_id?: string; attack_id?: string; risk_score?: number | null; reasons?: string | string[]; synthetic: boolean }
export type Attack = { id: string; name: string; severity: string; status: string; accounts: number; devices: number; merchants: number; transactions: number; created_at: string; attack_type?: string; attack_score?: number; detection_score?: number; evasion_success?: boolean; generation?: number; synthetic: boolean }
export type DashboardData = { metrics: { transactions_monitored: number; active_threats: number; attacks_simulated: number; mean_detection_score: number | null; false_positive_rate: number | null; average_detection_time: number | null }; transactions: Transaction[]; incidents: Incident[] }
export type RiskAnalysis = { risk_score: number; classification: string; signals: Record<string, number | boolean>; reasons: string[]; recommended_action: string }
export type Investigation = { finding: string; evidence: string[]; risk: string; attack_type: string; recommended_action: string; risk_score: number; signals: Record<string, number | boolean>; analysis_mode: string }
export type Simulation = { id: string; status: string; stage: number; detection_score: number | null; created_at: string; attack_id?: string }
export type AnalyticsData = { mean_detection_score: number | null; false_positive_rate: number | null; average_response_time: number | null; daily_events: { day: string; count: number }[]; model_version?: string | null }
export type AuditEvent = { id: number; event_type: string; entity_id: string; details: string; created_at: string }
export type ModelVersion = { id: number; version: string; training_samples: number; precision: number; recall: number; f1: number; created_at: string }
export type ThreatPattern = { id: number; name: string; description: string; severity: string }
export type NetworkData = { nodes: { id: string; name: string; city: string; type: string }[]; relationships: { from: string; to: string; type: string }[] }

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response
  try { response = await fetch(`${API_BASE}${path}`, { ...init, headers: { 'Content-Type': 'application/json', ...init?.headers } }) }
  catch (cause) { throw new ApiError('Unable to reach the EvoPay API. Check that the backend is running and the API URL is correct.', path, null, cause) }
  if (!response.ok) {
    let detail = `The EvoPay API returned ${response.status}.`
    try { const body = await response.json() as { detail?: string }; if (body.detail) detail = body.detail } catch { /* no JSON error body */ }
    throw new ApiError(detail, path, response.status)
  }
  try { return await response.json() as T } catch (cause) { throw new ApiError('The EvoPay API returned invalid JSON.', path, response.status, cause) }
}

export const api = {
  dashboard: () => request<DashboardData>('/dashboard'),
  transactions: (limit = 50, offset = 0) => request<Transaction[]>(`/transactions?limit=${limit}&offset=${offset}`),
  transaction: (id: string) => request<Transaction>(`/transactions/${id}`),
  risk: (id: string) => request<RiskAnalysis>(`/transactions/${id}/risk`),
  analyze: (id: string) => request<RiskAnalysis>(`/transactions/${id}/analyze`, { method: 'POST' }),
  action: (id: string, action: string) => request<{ transaction_id: string; status: string }>(`/transactions/${id}/action`, { method: 'POST', body: JSON.stringify({ action }) }),
  investigate: (id: string) => request<{ status: string; entity_id: string; notes?: string; investigation: Investigation }>('/investigate', { method: 'POST', body: JSON.stringify({ transaction_id: id }) }),
  network: () => request<NetworkData>('/network'),
  startSimulation: (attackId?: string) => request<Simulation>('/simulation/start', { method: 'POST', body: JSON.stringify({ attack_id: attackId }) }),
  simulation: (id: string) => request<Simulation>(`/simulation/${id}`),
  adaptDefense: (pattern: string) => request<{ before_detection_score: number | null; after_detection_score: number | null; model_version: string | null; pattern?: string }>('/defense/adapt', { method: 'POST', body: JSON.stringify({ pattern }) }),
  attacks: () => request<Attack[]>('/attacks'),
  generateAttack: (attackType: string) => { const typeMap: Record<string, string> = { 'Synthetic Identity': 'synthetic_identity', 'Account Takeover': 'account_takeover', 'Card Testing': 'card_testing', 'Money Mule Network': 'money_mule', 'Merchant Collusion': 'merchant_collusion', 'Behavioral Mimicry': 'behavioral_mimicry', 'Device Rotation': 'device_rotation', 'Refund Abuse': 'refund_abuse', 'Velocity Attack': 'velocity_attack', 'Composite Attack': 'composite_attack' }; return request<Attack>('/attacks/generate', { method: 'POST', body: JSON.stringify({ attack_type: typeMap[attackType] ?? 'composite_attack', strategy: attackType }) }) },
  evolveAttack: (attackId: string) => request<Attack>('/attacks/evolve', { method: 'POST', body: JSON.stringify({ attack_id: attackId }) }),
  incidents: (limit = 50, offset = 0) => request<Incident[]>(`/incidents?limit=${limit}&offset=${offset}`),
  incidentAction: (id: string, status: string) => request<{ id: string; status: string }>(`/incidents/${id}/action`, { method: 'POST', body: JSON.stringify({ status }) }),
  analytics: () => request<AnalyticsData>('/analytics'),
  modelVersions: () => request<ModelVersion[]>('/model-versions'),
  threatLibrary: () => request<ThreatPattern[]>('/threat-library'),
  addThreatPattern: (name: string, description: string, severity = 'MEDIUM') => request<ThreatPattern>('/threat-library', { method: 'POST', body: JSON.stringify({ name, description, severity }) }),
  audit: (limit = 100) => request<AuditEvent[]>(`/audit?limit=${limit}`),
}
