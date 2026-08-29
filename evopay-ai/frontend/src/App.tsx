import { useEffect, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import {
  Activity,
  ArrowUpRight,
  Bell,
  ChevronRight,
  Circle,
  CreditCard,
  Gauge,
  LayoutDashboard,
  LineChart,
  Network as NetworkIcon,
  Radar,
  Settings as SettingsIcon,
  ShieldCheck,
  SlidersHorizontal,
  Sparkles,
  Target,
  TriangleAlert,
  Zap,
} from 'lucide-react'
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
import { api } from './lib/api'

void Promise.all([api.dashboard(), api.transactions(), api.attacks(), api.incidents()])

type RouteConfig = { title: string; kicker: string; icon: typeof LayoutDashboard; description: string }
const routes: Record<string, RouteConfig> = {
  '/dashboard': { title: 'Command Center', kicker: 'Operational overview', icon: LayoutDashboard, description: 'Live defense posture across your payment network.' },
  '/red-team': { title: 'Red Team', kicker: 'Adversarial operations', icon: Target, description: 'Explore attack surfaces and emerging fraud patterns.' },
  '/simulation': { title: 'Attack Simulator', kicker: 'Controlled environment', icon: Radar, description: 'Simulation controls will appear here when the lab is connected.' },
  '/transactions': { title: 'Transactions', kicker: 'Payment intelligence', icon: CreditCard, description: 'Search and inspect payment events across every channel.' },
  '/network': { title: 'Fraud Network', kicker: 'Entity intelligence', icon: NetworkIcon, description: 'Map relationships between accounts, devices, and payment instruments.' },
  '/blue-team': { title: 'Blue Team', kicker: 'Defense operations', icon: ShieldCheck, description: 'Coordinate detection rules and mitigation workflows.' },
  '/incidents': { title: 'Incidents', kicker: 'Response queue', icon: TriangleAlert, description: 'Triage high-signal events and manage active investigations.' },
  '/analytics': { title: 'Analytics', kicker: 'Performance intelligence', icon: LineChart, description: 'Measure model performance and operational impact over time.' },
  '/settings': { title: 'Settings', kicker: 'Workspace configuration', icon: SettingsIcon, description: 'Manage team access, notifications, and defense preferences.' },
}
const trendData = [{ time: '00:00', blocked: 42, reviewed: 16 }, { time: '04:00', blocked: 58, reviewed: 23 }, { time: '08:00', blocked: 49, reviewed: 31 }, { time: '12:00', blocked: 84, reviewed: 28 }, { time: '16:00', blocked: 72, reviewed: 36 }, { time: '20:00', blocked: 96, reviewed: 42 }, { time: 'Now', blocked: 88, reviewed: 34 }]
const activity = [{ icon: Zap, title: 'Velocity anomaly blocked', detail: '14 cards · EU cluster', time: '2m ago', tone: 'cyan' }, { icon: TriangleAlert, title: 'New incident surfaced', detail: 'MFA fatigue pattern', time: '8m ago', tone: 'amber' }, { icon: ShieldCheck, title: 'Rule updated', detail: 'Device fingerprint v2.4', time: '21m ago', tone: 'green' }]

function GlassCard({ children, className = '' }: { children: React.ReactNode; className?: string }) { return <div className={`glass-card ${className}`}>{children}</div> }
function AnimatedNumber({ value }: { value: string }) { return <motion.span initial={{ opacity: 0, y: 4 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: .35 }}>{value}</motion.span> }
function MetricCard({ label, value, change, icon: Icon, tone = 'cyan' }: { label: string; value: string; change: string; icon: typeof Activity; tone?: string }) { return <GlassCard className="metric-card"><div className={`metric-icon ${tone}`}><Icon size={17} /></div><span className="metric-label">{label}</span><strong className="metric-value"><AnimatedNumber value={value} /></strong><span className={`metric-change ${tone}`}>{change}</span></GlassCard> }
function StatusBadge({ children, tone = 'green' }: { children: React.ReactNode; tone?: string }) { return <span className={`status-badge ${tone}`}><Circle size={6} fill="currentColor" />{children}</span> }
function RiskBadge({ children, tone = 'amber' }: { children: React.ReactNode; tone?: string }) { return <span className={`risk-badge ${tone}`}>{children}</span> }

function Dashboard({ navigate }: { navigate: (path: string) => void }) {
  return (
    <div className="dashboard-page">
      <div className="welcome-row">
        <div>
          <p className="eyebrow">Defense Posture <span>•</span> Live Monitoring</p>
          <h1>Defense Posture</h1>
          <p className="subheading">Your payment network is protected, continuously evaluated, and learning in real time.</p>
        </div>
        <button className="primary-button" onClick={() => navigate('/red-team')}>
          <Sparkles size={16} /> Open Red Team Lab
        </button>
      </div>

      <div className="metric-grid">
        <MetricCard label="Protected volume" value="$2.84M" change="↑ 12.8% vs last 24h" icon={CreditCard} />
        <MetricCard label="Threats blocked" value="1,284" change="↑ 18.4% vs last 24h" icon={ShieldCheck} tone="green" />
        <MetricCard label="Precision rate" value="99.72%" change="↑ 0.08% this week" icon={Gauge} tone="blue" />
        <MetricCard label="Active incidents" value="07" change="2 need attention" icon={TriangleAlert} tone="amber" />
      </div>

      <div className="dashboard-grid">
        <section className="chart-card glass-card">
          <div className="section-heading">
            <div>
              <p className="eyebrow">Network telemetry</p>
              <h2>Defense activity</h2>
            </div>
            <div className="chart-legend">
              <span><i className="dot cyan" />Blocked</span>
              <span><i className="dot muted" />Reviewed</span>
              <button className="icon-button" aria-label="Chart settings"><SlidersHorizontal size={16} /></button>
            </div>
          </div>
          <div className="chart-summary">
            <strong>2,891</strong>
            <span>events processed <b>+14.2%</b></span>
          </div>
          <div className="chart-wrap">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={trendData}>
                <defs>
                  <linearGradient id="blockedFill" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#43d9e6" stopOpacity={0.28} />
                    <stop offset="100%" stopColor="#43d9e6" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="time" axisLine={false} tickLine={false} tick={{ fill: '#6c7b91', fontSize: 11 }} />
                <YAxis hide />
                <Tooltip contentStyle={{ background: '#111d2e', border: '1px solid #263b50', borderRadius: 8, color: '#f5f8fb' }} />
                <Area type="monotone" dataKey="blocked" stroke="#43d9e6" strokeWidth={2} fill="url(#blockedFill)" />
                <Area type="monotone" dataKey="reviewed" stroke="#657489" strokeWidth={1.5} fill="none" strokeDasharray="4 4" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </section>

        <section className="activity-card glass-card">
          <div className="section-heading">
            <div>
              <p className="eyebrow">Signal stream</p>
              <h2>Recent activity</h2>
            </div>
            <button className="text-button" onClick={() => navigate('/transactions')}>
              View all <ChevronRight size={15} />
            </button>
          </div>
          <div className="activity-list">
            {activity.map((item) => {
              const Icon = item.icon
              return (
                <div className="activity-item" key={item.title}>
                  <div className={`activity-icon ${item.tone}`}><Icon size={16} /></div>
                  <div className="activity-copy">
                    <strong>{item.title}</strong>
                    <span>{item.detail}</span>
                  </div>
                  <time>{item.time}</time>
                </div>
              )
            })}
          </div>
          <div className="stream-footer">
            <Activity size={14} /> Ingesting 4,280 events / min <span className="pulse-dot" />
          </div>
        </section>
      </div>

      <div className="lower-grid">
        <section className="coverage-card glass-card">
          <div className="section-heading">
            <div>
              <p className="eyebrow">Autonomous coverage</p>
              <h2>Defense layers</h2>
            </div>
            <StatusBadge>All systems nominal</StatusBadge>
          </div>
          {[
            ['Transaction scoring', '99.8%', 'green'],
            ['Device intelligence', '97.4%', 'cyan'],
            ['Graph detection', '91.6%', 'blue'],
          ].map(([name, value, tone]) => (
            <div className="coverage-row" key={name}>
              <span>{name}</span>
              <div className="progress"><i className={tone} style={{ width: value }} /></div>
              <strong>{value}</strong>
            </div>
          ))}
        </section>

        <section className="queue-card glass-card">
          <div className="section-heading">
            <div>
              <p className="eyebrow">Requires review</p>
              <h2>Priority queue</h2>
            </div>
            <RiskBadge>02 elevated</RiskBadge>
          </div>
          <div className="queue-row" style={{ cursor: 'pointer' }} onClick={() => navigate('/incidents')}>
            <div className="queue-avatar">MC</div>
            <div>
              <strong>Merchant cluster anomaly</strong>
              <span>Cross-border velocity spike</span>
            </div>
            <RiskBadge tone="red">High</RiskBadge>
          </div>
          <div className="queue-row" style={{ cursor: 'pointer' }} onClick={() => navigate('/incidents')}>
            <div className="queue-avatar purple">DV</div>
            <div>
              <strong>Device reuse pattern</strong>
              <span>9 accounts · 3 instruments</span>
            </div>
            <RiskBadge>Medium</RiskBadge>
          </div>
        </section>
      </div>
    </div>
  )
}

function TopBar({ config }: { config: RouteConfig }) {
  return (
    <header className="top-bar">
      <div className="mobile-title">
        <config.icon size={16} />
        {config.title}
      </div>
      <div className="top-status">
        <StatusBadge>Live</StatusBadge>
        <span className="simulation">
          <span className="sim-dot" /> Simulation idle
        </span>
      </div>
      <div className="top-actions">
        <button className="icon-button" aria-label="Notifications">
          <Bell size={18} />
          <b className="notification-dot" />
        </button>
        <div className="user-chip">
          <div className="user-avatar">AK</div>
          <span>Alex Kim</span>
          <ChevronRight size={14} />
        </div>
      </div>
    </header>
  )
}

function App() {
  const [path, setPath] = useState(window.location.pathname in routes ? window.location.pathname : '/dashboard')

  useEffect(() => {
    const onPop = () => setPath(window.location.pathname in routes ? window.location.pathname : '/dashboard')
    window.addEventListener('popstate', onPop)
    return () => window.removeEventListener('popstate', onPop)
  }, [])

  const navigate = (nextPath: string) => {
    window.history.pushState({}, '', nextPath)
    setPath(nextPath)
  }

  const config = routes[path] ?? routes['/dashboard']

  return (
    <AppShell path={path} onNavigate={navigate}>
      <TopBar config={config} />
      <AnimatePresence mode="wait">
        <motion.main
          key={path}
          className="page-content"
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -6 }}
          transition={{ duration: 0.22 }}
        >
          {path === '/dashboard' && <Dashboard navigate={navigate} />}
          {path === '/red-team' && <CommandDashboard navigate={navigate} />}
          {path === '/simulation' && <Simulation />}
          {path === '/transactions' && <Transactions />}
          {path === '/network' && <Network />}
          {path === '/blue-team' && <BlueTeam />}
          {path === '/incidents' && <Incidents />}
          {path === '/analytics' && <Analytics />}
          {path === '/settings' && <Settings />}
        </motion.main>
      </AnimatePresence>
    </AppShell>
  )
}

export default App
