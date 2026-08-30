import { useEffect, useState } from 'react'
import { Activity, BrainCircuit, Network, ShieldAlert } from 'lucide-react'
import { api, type RiskAnalysis, type Transaction } from '../lib/api'

export default function BlueTeam() {
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [selected, setSelected] = useState('')
  const [analysis, setAnalysis] = useState<RiskAnalysis | null>(null)
  const [error, setError] = useState<string | null>(null)
  useEffect(() => { api.transactions().then((items) => { setTransactions(items); setSelected(items[0]?.id ?? '') }).catch((reason: Error) => setError(reason.message)) }, [])
  useEffect(() => { if (!selected) { setAnalysis(null); return }; setAnalysis(null); api.risk(selected).then(setAnalysis).catch((reason: Error) => setError(reason.message)) }, [selected])
  const scores = analysis ? [['ML score', Number(analysis.signals.ml_score ?? 0), BrainCircuit], ['Behavior score', Number(analysis.signals.behavior_score ?? 0), Activity], ['Anomaly score', Number(analysis.signals.anomaly_score ?? 0), ShieldAlert], ['Graph score', Number(analysis.signals.graph_score ?? 0), Network]] as const : []
  return <div className="blue-team-page"><div className="page-header"><div><p className="eyebrow">BLUE TEAM · Deterministic analysis</p><h1>Defense Operations</h1><p className="subheading">Inspect scores calculated for recorded synthetic transactions. No module uptime, learning status, or performance claim is inferred.</p></div></div>
    {error && <div className="error-state" style={{ padding: 20 }}>{error}</div>}
    <section className="risk-engine glass-card"><div className="section-heading"><div><p className="eyebrow">Transaction</p><h2>Risk Engine Visualization</h2></div><select value={selected} onChange={(event) => setSelected(event.target.value)}><option value="">No transactions</option>{transactions.map((item) => <option key={item.id} value={item.id}>{item.id}</option>)}</select></div>
      {!selected && <div className="empty-state">No transactions are available for analysis.</div>}
      {selected && !analysis && !error && <div className="loading-state">Calculating stored transaction risk</div>}
      {analysis && <><div className="risk-layout"><div className="risk-gauge"><div className="gauge-ring" style={{ '--risk-angle': `${analysis.risk_score * 1.8}deg` } as React.CSSProperties}><div><strong>{analysis.risk_score}</strong><span>FINAL RISK</span></div></div><b className={`risk-verdict ${analysis.classification.toLowerCase()}`}>{analysis.classification}</b></div><div className="score-list">{scores.map(([label, value, Icon]) => <div className="score-bar-row" key={label}><div><span><Icon size={13} /> {label}</span><strong>{value}</strong></div><div className="score-bar"><i style={{ width: `${value}%` }} /></div></div>)}</div></div><div className="reason-list">{analysis.reasons.map((reason) => <div key={reason}><ShieldAlert size={15} /><span>{reason}</span></div>)}{!analysis.reasons.length && <div className="empty-state">No policy thresholds were exceeded.</div>}</div></>}
    </section>
  </div>
}
