import { ReactNode, useEffect, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { Blocks, CircleGauge, CreditCard, GitBranch, LayoutDashboard, LineChart, Network, Radar, RotateCcw, Settings, ShieldCheck, Target, TriangleAlert, X, Zap } from 'lucide-react'

const nav = [{ label: 'Command Center', path: '/dashboard', icon: LayoutDashboard }, { label: 'Red Team', path: '/red-team', icon: Target, group: true }, { label: 'Attack Simulator', path: '/simulation', icon: Radar }, { label: 'Transactions', path: '/transactions', icon: CreditCard }, { label: 'Fraud Network', path: '/network', icon: Network }, { label: 'Blue Team', path: '/blue-team', icon: ShieldCheck, group: true }, { label: 'Incidents', path: '/incidents', icon: TriangleAlert }, { label: 'Analytics', path: '/analytics', icon: LineChart }]
const demoSteps = [
 { path: '/dashboard', label: 'Command Center', detail: 'Review recorded simulation counts, activity, and empty states.' },
 { path: '/red-team', label: 'Red Team Lab', detail: 'Choose a controlled attack configuration or inspect stored synthetic attacks.' },
 { path: '/simulation', label: 'Attack Simulator', detail: 'Start a simulation run; outcomes remain Not evaluated until the backend records evidence.' },
 { path: '/transactions', label: 'Transactions', detail: 'Inspect synthetic transaction records and their current server decisions.' },
 { path: '/network', label: 'Fraud Network', detail: 'Review relationships derived from stored transaction records.' },
 { path: '/blue-team', label: 'Blue Team', detail: 'Inspect deterministic scores for a selected recorded transaction.' },
 { path: '/incidents', label: 'Incidents', detail: 'Review incidents and audit events that exist in the database.' },
 { path: '/analytics', label: 'Analytics', detail: 'Review measured values; unavailable performance remains Not evaluated.' },
]

function DemoOverlay({ step, restart, stop }: { step: number; restart: () => void; stop: () => void }) { const current = demoSteps[step]; const isComplete = step === demoSteps.length - 1; return <AnimatePresence><motion.div className="demo-overlay" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}><motion.section className="demo-console glass-card" initial={{ opacity: 0, y: 18, scale: .98 }} animate={{ opacity: 1, y: 0, scale: 1 }}><div className="demo-console-top"><div><span className="demo-eyebrow"><Zap size={12} /> Guided interface tour</span><h2>{isComplete ? 'Tour complete' : current.label}</h2></div><button className="demo-close" onClick={stop} aria-label="Stop tour"><X size={17} /></button></div><p className="demo-detail">{isComplete ? 'Run a simulation to create measured results.' : current.detail}</p><div className="demo-progress"><div><span>Tour sequence</span><strong>{step + 1} / {demoSteps.length}</strong></div><i><b style={{ width: `${((step + 1) / demoSteps.length) * 100}%` }} /></i></div><div className="demo-milestones">{demoSteps.map((item, index) => <div className={`${index < step ? 'done' : ''} ${index === step ? 'current' : ''}`} key={`${item.label}-${index}`}><span>{index < step ? '✓' : index + 1}</span><small>{item.label}</small></div>)}</div><button className="demo-restart" onClick={restart}><RotateCcw size={14} /> Restart tour</button></motion.section></motion.div></AnimatePresence> }

export function AppShell({ children, path, onNavigate }: { children: ReactNode; path: string; onNavigate: (path: string) => void }) {
 const [demoStep, setDemoStep] = useState<number | null>(null)
 const startDemo = () => { setDemoStep(0); onNavigate('/dashboard') }
 const restartDemo = () => { setDemoStep(0); onNavigate('/dashboard') }
 const stopDemo = () => setDemoStep(null)
 useEffect(() => { if (demoStep === null || demoStep >= demoSteps.length - 1) return; const timer = window.setTimeout(() => { const next = demoStep + 1; setDemoStep(next); onNavigate(demoSteps[next].path) }, 12000); return () => window.clearTimeout(timer) }, [demoStep, onNavigate])
 return <div className="app-shell"><aside className="sidebar"><div className="brand"><div className="brand-symbol"><Blocks size={17} /></div><span>EvoPay <b>Lab</b></span></div><div className="workspace-label">Adversarial payments</div><nav>{nav.map((item) => { const Icon = item.icon; return <button key={item.path} className={`nav-item ${path === item.path ? 'active' : ''} ${item.group ? 'group-start' : ''}`} onClick={() => onNavigate(item.path)}><Icon size={17} /><span>{item.label}</span>{path === item.path && <i />}</button> })}</nav><div className="sidebar-bottom"><button className="run-demo-button" onClick={startDemo}><Zap size={15} /> Guided tour</button><button className="nav-item" onClick={() => onNavigate('/settings')}><Settings size={17} /><span>Settings</span></button><div className="sidebar-footer"><span><CircleGauge size={14} /> Research preview</span><span><GitBranch size={13} /> Synthetic only</span></div></div></aside><section className="main-pane">{children}</section>{demoStep !== null && <DemoOverlay step={demoStep} restart={restartDemo} stop={stopDemo} />}</div>
}
