import { useEffect, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { Activity, Bell, ChevronRight, Circle, CreditCard, Gauge, LayoutDashboard, LineChart, Network as NetworkIcon, Radar, Settings as SettingsIcon, ShieldCheck, Sparkles, Target, TriangleAlert } from 'lucide-react'
import { Area, AreaChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { AppShell } from './layouts/AppShell'
import CommandDashboard from './pages/Dashboard'
import BlueTeam from './pages/BlueTeam'
import Network from './pages/Network'
import Simulation from './pages/Simulation'
import Transactions from './pages/Transactions'
import Incidents from './pages/Incidents'
import Analytics from './pages/Analytics'
import Settings from './pages/Settings'
import { api, type DashboardData } from './lib/api'

type RouteConfig = { title: string; kicker: string; icon: typeof LayoutDashboard; description: string }
const routes: Record<string, RouteConfig> = {
  '/dashboard': { title: 'Command Center', kicker: 'Operational overview', icon: LayoutDashboard, description: 'Recorded simulation activity.' },
  '/red-team': { title: 'Red Team', kicker: 'Adversarial operations', icon: Target, description: 'Explore controlled fraud simulations.' },
  '/simulation': { title: 'Attack Simulator', kicker: 'Controlled environment', icon: Radar, description: 'Run synthetic attack scenarios.' },
  '/transactions': { title: 'Transactions', kicker: 'Payment intelligence', icon: CreditCard, description: 'Inspect recorded synthetic payment events.' },
  '/network': { title: 'Fraud Network', kicker: 'Entity intelligence', icon: NetworkIcon, description: 'Map recorded entity relationships.' },
  '/blue-team': { title: 'Blue Team', kicker: 'Defense operations', icon: ShieldCheck, description: 'Inspect deterministic risk decisions.' },
  '/incidents': { title: 'Incidents', kicker: 'Response queue', icon: TriangleAlert, description: 'Manage recorded investigations.' },
  '/analytics': { title: 'Analytics', kicker: 'Measured results', icon: LineChart, description: 'Review metrics supported by stored records.' },
  '/settings': { title: 'Settings', kicker: 'Workspace configuration', icon: SettingsIcon, description: 'Manage local workspace preferences.' },
}

function GlassCard({ children, className = '' }: { children: React.ReactNode; className?: string }) { return <div className={`glass-card ${className}`}>{children}</div> }
function MetricCard({ label, value, note, icon: Icon, tone = 'cyan' }: { label: string; value: string; note: string; icon: typeof Activity; tone?: string }) { return <GlassCard className="metric-card"><div className={`metric-icon ${tone}`}><Icon size={17} /></div><span className="metric-label">{label}</span><strong className="metric-value"><motion.span initial={{ opacity: 0 }} animate={{ opacity: 1 }}>{value}</motion.span></strong><span className={`metric-change ${tone}`}>{note}</span></GlassCard> }
function RiskBadge({ children, tone = 'amber' }: { children: React.ReactNode; tone?: string }) { return <span className={`risk-badge ${tone}`}>{children}</span> }

function Dashboard({ navigate }: { navigate: (path: string) => void }) {
  const [data, setData] = useState<DashboardData | null>(null)
  const [error, setError] = useState<string | null>(null)
  useEffect(() => { api.dashboard().then(setData).catch((reason: Error) => setError(reason.message)) }, [])
  if (error) return <div className="dashboard-page"><div className="welcome-row"><div><p className="eyebrow">Command center</p><h1>Defense posture</h1></div></div><section className="glass-card error-state" style={{ padding: 32 }}><TriangleAlert size={22} /><h2>Dashboard unavailable</h2><p>{error}</p><button className="primary-button" onClick={() => window.location.reload()}>Retry connection</button></section></div>
  if (!data) return <div className="dashboard-page"><div className="welcome-row"><div><p className="eyebrow">Command center</p><h1>Defense posture</h1></div></div><section className="glass-card loading-state" style={{ padding: 32 }}>Loading recorded simulation data</section></div>
  const notEvaluated = 'Not evaluated'
  const blocked = data.transactions.filter((item) => item.status === 'BLOCKED').length
  const reviewed = data.transactions.filter((item) => ['VERIFY', 'HOLD'].includes(item.status)).length
  const chartData = [...data.transactions].reverse().map((item) => ({ time: new Date(item.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }), blocked: item.status === 'BLOCKED' ? 1 : 0, reviewed: ['VERIFY', 'HOLD'].includes(item.status) ? 1 : 0 }))
  const priority = data.incidents.filter((item) => item.status !== 'RESOLVED').slice(0, 3)
  const recent = [...data.incidents.map((item) => ({ id: item.id, title: item.title, detail: `${item.severity} · ${item.status}`, createdAt: item.created_at })), ...data.transactions.map((item) => ({ id: item.id, title: `${item.status.toLowerCase()} transaction`, detail: `Risk ${item.risk_score} · synthetic`, createdAt: item.created_at }))].sort((a, b) => b.createdAt.localeCompare(a.createdAt)).slice(0, 4)
  const outcomes: [string, number, string][] = [['Blocked', blocked, 'green'], ['Review or hold', reviewed, 'cyan'], ['Other statuses', data.transactions.length - blocked - reviewed, 'blue']]
  return <div className="dashboard-page">
    <div className="welcome-row"><div><p className="eyebrow">Recorded simulation posture</p><h1>Defense Posture</h1><p className="subheading">Database-backed results from synthetic payment experiments. No production payment network is connected.</p></div><button className="primary-button" onClick={() => navigate('/red-team')}><Sparkles size={16} /> Open Red Team Lab</button></div>
    <div className="metric-grid"><MetricCard label="Synthetic transactions" value={data.metrics.transactions_monitored.toLocaleString()} note="recorded in database" icon={CreditCard} /><MetricCard label="Blocked transactions" value={blocked.toLocaleString()} note="current recorded status" icon={ShieldCheck} tone="green" /><MetricCard label="Mean heuristic detection score" value={data.metrics.mean_detection_score === null ? notEvaluated : `${data.metrics.mean_detection_score} / 100`} note={data.metrics.mean_detection_score === null ? 'insufficient attack data' : 'configured attack heuristics; not a measured rate'} icon={Gauge} tone="blue" /><MetricCard label="Active incidents" value={data.metrics.active_threats.toLocaleString()} note="unresolved records" icon={TriangleAlert} tone="amber" /></div>
    <div className="dashboard-grid"><section className="chart-card glass-card"><div className="section-heading"><div><p className="eyebrow">Recorded outcomes</p><h2>Transaction activity</h2></div></div><div className="chart-summary"><strong>{data.transactions.length}</strong><span>transactions shown</span></div>{chartData.length ? <div className="chart-wrap"><ResponsiveContainer width="100%" height="100%"><AreaChart data={chartData}><XAxis dataKey="time" axisLine={false} tickLine={false} /><YAxis hide /><Tooltip /><Area type="monotone" dataKey="blocked" stroke="#c8f36a" fill="none" /><Area type="monotone" dataKey="reviewed" stroke="#94958b" fill="none" /></AreaChart></ResponsiveContainer></div> : <div className="empty-state">No transactions have been recorded.</div>}</section>
    <section className="activity-card glass-card"><div className="section-heading"><div><p className="eyebrow">Database records</p><h2>Recent activity</h2></div><button className="text-button" onClick={() => navigate('/transactions')}>View all <ChevronRight size={15} /></button></div><div className="activity-list">{recent.map((item) => <div className="activity-item" key={item.id}><div className="activity-icon cyan"><Activity size={16} /></div><div className="activity-copy"><strong>{item.title}</strong><span>{item.detail}</span></div><time>{new Date(item.createdAt).toLocaleString()}</time></div>)}</div>{!recent.length && <div className="empty-state">No activity has been recorded yet.</div>}</section></div>
    <div className="lower-grid"><section className="coverage-card glass-card"><div className="section-heading"><div><p className="eyebrow">Recorded outcomes</p><h2>Transaction disposition</h2></div><span className="status-badge green"><Circle size={6} />{data.transactions.length ? 'Data available' : 'Awaiting data'}</span></div>{outcomes.map(([name, count, tone]) => { const value = data.transactions.length ? `${Math.round(count / data.transactions.length * 100)}%` : '0%'; return <div className="coverage-row" key={name}><span>{name}</span><div className="progress"><i className={tone} style={{ width: value }} /></div><strong>{value}</strong></div> })}</section>
    <section className="queue-card glass-card"><div className="section-heading"><div><p className="eyebrow">Requires review</p><h2>Priority queue</h2></div><RiskBadge>{priority.length} open</RiskBadge></div>{priority.map((incident) => <div className="queue-row" key={incident.id} onClick={() => navigate('/incidents')}><div className="queue-avatar">{incident.severity.slice(0, 2)}</div><div><strong>{incident.title}</strong><span>{incident.id} · {incident.status}</span></div><RiskBadge tone={incident.severity === 'CRITICAL' ? 'red' : 'amber'}>{incident.severity}</RiskBadge></div>)}{!priority.length && <div className="empty-state">No unresolved incidents.</div>}</section></div>
  </div>
}

function TopBar({ config }: { config: RouteConfig }) { return <header className="top-bar"><div className="mobile-title"><config.icon size={16} />{config.title}</div><div className="top-context"><span>{config.kicker}</span><b>Controlled environment</b></div><div className="top-actions"><button className="icon-button" aria-label="Notifications"><Bell size={18} /></button><div className="user-chip"><div className="user-avatar">EV</div><span>Workspace</span><ChevronRight size={14} /></div></div></header> }

function App() {
  const [path, setPath] = useState(window.location.pathname in routes ? window.location.pathname : '/dashboard')
  useEffect(() => { const onPop = () => setPath(window.location.pathname in routes ? window.location.pathname : '/dashboard'); window.addEventListener('popstate', onPop); return () => window.removeEventListener('popstate', onPop) }, [])
  const navigate = (nextPath: string) => { window.history.pushState({}, '', nextPath); setPath(nextPath) }
  const config = routes[path] ?? routes['/dashboard']
  return <AppShell path={path} onNavigate={navigate}><TopBar config={config} /><AnimatePresence mode="wait"><motion.main key={path} className="page-content" initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -6 }} transition={{ duration: .22 }}>{path === '/dashboard' && <Dashboard navigate={navigate} />}{path === '/red-team' && <CommandDashboard navigate={navigate} />}{path === '/simulation' && <Simulation />}{path === '/transactions' && <Transactions />}{path === '/network' && <Network />}{path === '/blue-team' && <BlueTeam />}{path === '/incidents' && <Incidents />}{path === '/analytics' && <Analytics />}{path === '/settings' && <Settings />}</motion.main></AnimatePresence></AppShell>
}
export default App
