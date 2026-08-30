import { useEffect, useMemo, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { ArrowUpRight, Ban, Check, Clock3, Filter, MapPin, RefreshCw, Search, ShieldAlert, Sparkles, User, X } from 'lucide-react'
import { api, type Investigation, type RiskAnalysis, type Transaction } from '../lib/api'

type StatusFilter = 'ALL' | 'ALLOWED' | 'VERIFY' | 'HOLD' | 'BLOCKED'

function DetailDrawer({
  txn,
  close,
  onUpdateStatus,
}: {
  txn: Transaction
  close: () => void
  onUpdateStatus: (id: string, nextStatus: string) => void
}) {
  const [analysis, setAnalysis] = useState<RiskAnalysis | null>(null)
  const [investigation, setInvestigation] = useState<Investigation | null>(null)
  const [investigating, setInvestigating] = useState(false)
  const [acting, setActing] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    setAnalysis(null)
    setInvestigation(null)
    api.risk(txn.id).then(setAnalysis).catch((reason: Error) => setError(reason.message))
  }, [txn.id])

  const riskScore = analysis?.risk_score ?? txn.risk_score
  const classification = analysis?.classification ?? (riskScore > 80 ? 'CRITICAL' : riskScore > 60 ? 'HIGH' : riskScore > 30 ? 'MEDIUM' : 'LOW')

  const handleAction = async (action: string) => {
    setActing(true)
    try {
      const res = await api.action(txn.id, action)
      onUpdateStatus(txn.id, res.status)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'The action could not be saved.')
    } finally {
      setActing(false)
    }
  }

  const runInvestigation = async () => {
    setInvestigating(true)
    try {
      const res = await api.investigate(txn.id)
      setInvestigation(res.investigation)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'The investigation could not be opened.')
    } finally {
      setInvestigating(false)
    }
  }

  const details = [
    ['Transaction ID', txn.id],
    ['Customer ID', txn.customer_id],
    ['Merchant ID', txn.merchant_id],
    ['Amount', `₹${txn.amount.toLocaleString('en-IN')}`],
    ['Location', `${txn.location}, India`],
    ['Payment method', txn.payment_method],
    ['Device ID', txn.device_id],
    ['Timestamp', txn.created_at],
  ]

  return (
    <motion.aside
      className="detail-drawer"
      initial={{ x: '100%' }}
      animate={{ x: 0 }}
      exit={{ x: '100%' }}
      transition={{ type: 'spring', damping: 25 }}
    >
      <div className="drawer-header">
        <div>
          <p className="eyebrow">Transaction Intelligence</p>
          <h2>{txn.id}</h2>
        </div>
        <button className="drawer-close" onClick={close} aria-label="Close details">
          <X size={18} />
        </button>
      </div>

      <div className="drawer-risk">
        <span>Risk Engine Score · {classification}</span>
        <strong>{riskScore}</strong>
        <div className="risk-meter">
          <i style={{ width: `${riskScore}%` }} />
        </div>
      </div>

      {analysis?.signals && (
        <div className="score-list" style={{ margin: '14px 0 20px' }}>
          <div className="score-bar-row">
            <div><span>ML Fraud Classifier</span><strong>{analysis.signals.ml_score == null ? 'Not evaluated' : Number(analysis.signals.ml_score)}</strong></div>
<div className="score-bar"><i className="cyan" style={{ width: `${Number(analysis.signals.ml_score ?? 0)}%` }} /></div>
          </div>
          <div className="score-bar-row">
            <div><span>Anomaly Detection</span><strong>{analysis.signals.anomaly_score == null ? 'Not evaluated' : Number(analysis.signals.anomaly_score)}</strong></div>
<div className="score-bar"><i className="red" style={{ width: `${Number(analysis.signals.anomaly_score ?? 0)}%` }} /></div>
          </div>
          <div className="score-bar-row">
            <div><span>Behavioral Scoring</span><strong>{analysis.signals.behavior_score == null ? 'Not evaluated' : Number(analysis.signals.behavior_score)}</strong></div>
<div className="score-bar"><i className="amber" style={{ width: `${Number(analysis.signals.behavior_score ?? 0)}%` }} /></div>
          </div>
          <div className="score-bar-row">
            <div><span>Graph Relationship</span><strong>{analysis.signals.graph_score == null ? 'Not evaluated' : Number(analysis.signals.graph_score)}</strong></div>
<div className="score-bar"><i className="purple" style={{ width: `${Number(analysis.signals.graph_score ?? 0)}%` }} /></div>
          </div>
        </div>
      )}

      <div className="detail-list">
        {details.map(([label, value]) => (
          <div key={label}>
            <span>{label}</span>
            <strong>{value}</strong>
          </div>
        ))}
      </div>

      <div className="flag-reasons">
        <h3>Explainability Signals</h3>
        {(analysis?.reasons ?? []).map((reason) => (
          <p key={reason}>
            <ShieldAlert size={15} /> {reason}
          </p>
        ))}
      </div>
      {error && <div className="error-state" style={{ padding: 12, marginTop: 12 }}>{error}</div>}

      {investigation && (
        <div className="glass-card" style={{ padding: '14px', margin: '18px 0', borderColor: '#2f6270' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px', color: '#57dcdb' }}>
            <Sparkles size={15} />
            <strong style={{ fontSize: '12px' }}>AI Investigator Finding</strong>
          </div>
          <p style={{ margin: '0 0 8px', fontSize: '11px', color: '#cadbe7', lineHeight: '1.45' }}>
            {investigation.finding}
          </p>
          <div style={{ fontSize: '10px', color: '#7b92a5' }}>
            Attack Type: <b style={{ color: '#e4b258' }}>{investigation.attack_type}</b> · Recommended: <b style={{ color: '#ef747b' }}>{investigation.recommended_action}</b>
          </div>
        </div>
      )}

      <div style={{ marginTop: '16px', display: 'flex', gap: '8px' }}>
        <button
          className="secondary-button"
          style={{ width: '100%', justifyContent: 'center' }}
          onClick={runInvestigation}
          disabled={investigating}
        >
          <Sparkles size={14} /> {investigating ? 'Analyzing Signals...' : 'Run AI Investigation'}
        </button>
      </div>

      <div style={{ marginTop: '20px' }}>
        <span style={{ display: 'block', marginBottom: '8px', color: '#71879c', fontSize: '10px', textTransform: 'uppercase', letterSpacing: '.08em' }}>
          Execute Mitigation Decision
        </span>
        <div className="drawer-actions">
          {(['ALLOW', 'VERIFY', 'HOLD', 'BLOCK'] as const).map((act) => {
            const isCurrent = txn.status.toUpperCase() === (act === 'ALLOW' ? 'ALLOWED' : act === 'BLOCK' ? 'BLOCKED' : act)
            return (
              <button
                key={act}
                className={isCurrent ? 'selected' : ''}
                onClick={() => handleAction(act)}
                disabled={acting}
              >
                {act === 'ALLOW' ? <Check size={13} /> : act === 'VERIFY' ? <ShieldAlert size={13} /> : act === 'HOLD' ? <Clock3 size={13} /> : <Ban size={13} />}
                {act}
              </button>
            )
          })}
        </div>
      </div>
    </motion.aside>
  )
}

export default function Transactions() {
  const [items, setItems] = useState<Transaction[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(false)
  const [filter, setFilter] = useState<StatusFilter>('ALL')
  const [search, setSearch] = useState('')
  const [selected, setSelected] = useState<Transaction | null>(null)

  const load = () => {
    setLoading(true)
    setError(false)
    api.transactions(100, 0)
      .then((data) => {
        setItems(data)
      })
      .catch(() => setError(true))
      .finally(() => setLoading(false))
  }

  useEffect(load, [])

  const handleUpdateStatus = (id: string, status: string) => {
    setItems((curr) => curr.map((item) => (item.id === id ? { ...item, status } : item)))
    if (selected && selected.id === id) {
      setSelected({ ...selected, status })
    }
  }

  const filteredItems = useMemo(() => {
    return items.filter((txn) => {
      const matchFilter =
        filter === 'ALL' ||
        (filter === 'ALLOWED' && txn.status === 'ALLOWED') ||
        (filter === 'BLOCKED' && txn.status === 'BLOCKED') ||
        (filter === 'VERIFY' && txn.status === 'VERIFY') ||
        (filter === 'HOLD' && txn.status === 'HOLD')

      const q = search.toLowerCase().trim()
      const matchSearch =
        !q ||
        txn.id.toLowerCase().includes(q) ||
        txn.customer_id.toLowerCase().includes(q) ||
        txn.merchant_id.toLowerCase().includes(q) ||
        txn.location.toLowerCase().includes(q) ||
        txn.payment_method.toLowerCase().includes(q)

      return matchFilter && matchSearch
    })
  }, [items, filter, search])

  return (
    <div className="data-page">
      <div className="data-page-heading" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: '24px' }}>
        <div>
<p className="eyebrow">Payment Intelligence <span>•</span> Recorded synthetic data</p>
          <h1 style={{ margin: 0, fontSize: '32px', fontWeight: 500 }}>Transactions</h1>
          <p className="subheading">Inspect synthetic payment events, signal evaluations, and server decisions.</p>
        </div>
        <button className="secondary-button" onClick={load}>
          <RefreshCw size={14} className={loading ? 'pulse-dot' : ''} /> Refresh Stream
        </button>
      </div>

      <div style={{ display: 'flex', gap: '12px', marginBottom: '16px', flexWrap: 'wrap', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', background: '#0e2234', border: '1px solid #1f374c', padding: '0 12px', borderRadius: '6px', height: '36px', width: 'min(320px, 100%)' }}>
          <Search size={14} color="#657d92" />
          <input
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by ID, customer, merchant, city..."
            style={{ border: 0, background: 'transparent', outline: 'none', color: '#e3edf3', fontSize: '11px', width: '100%', fontFamily: 'DM Mono, monospace' }}
          />
          {search && (
            <button onClick={() => setSearch('')} style={{ border: 0, background: 'transparent', color: '#748b9f', padding: 0 }}>
              <X size={13} />
            </button>
          )}
        </div>

        <div style={{ display: 'flex', gap: '6px', background: '#0a1a2b', padding: '3px', borderRadius: '6px', border: '1px solid #1c3245' }}>
          {(['ALL', 'BLOCKED', 'VERIFY', 'HOLD', 'ALLOWED'] as StatusFilter[]).map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              style={{
                height: '28px',
                padding: '0 12px',
                border: 0,
                borderRadius: '4px',
                fontSize: '10px',
                fontFamily: 'DM Mono, monospace',
                background: filter === f ? '#184755' : 'transparent',
                color: filter === f ? '#e5f8fa' : '#72869a',
                transition: '.15s ease',
              }}
            >
              {f}
            </button>
          ))}
        </div>
      </div>

      <section className="glass-card" style={{ padding: '4px 0', overflow: 'hidden' }}>
        <div className="transaction-table" style={{ margin: 0 }}>
          <div className="transaction-header" style={{ borderBottom: '1px solid #1b3042', padding: '12px 16px' }}>
            <span>Transaction ID</span>
            <span>Customer</span>
            <span>Merchant</span>
            <span>Amount</span>
            <span>Location</span>
            <span>Risk Score</span>
            <span>Decision</span>
          </div>

          {loading && <div style={{ padding: '36px', textAlign: 'center' }} className="loading-state">Loading synthetic transaction stream</div>}
{error && <div style={{ padding: '24px', textAlign: 'center', color: '#ef747b' }} className="error-state">Transaction API unavailable. No substitute data is being shown.</div>}

          {!loading && filteredItems.length === 0 && (
            <div style={{ padding: '48px 24px', textAlign: 'center', color: '#6e8396', fontSize: '12px' }}>
              No transactions match the selected filter or search query.
            </div>
          )}

          {!loading && (
            <AnimatePresence initial={false}>
              {filteredItems.map((txn) => {
                const statusClass = txn.status.toLowerCase()
                const risk = txn.risk_score
                return (
                  <motion.button
                    layout
                    key={txn.id}
                    className="transaction-row"
                    onClick={() => setSelected(txn)}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    style={{ padding: '12px 16px', cursor: 'pointer' }}
                  >
                    <span className="txn-id">{txn.id}</span>
                    <span>{txn.customer_id}</span>
                    <span>{txn.merchant_id}</span>
                    <span className="amount">₹{txn.amount.toLocaleString('en-IN')}</span>
                    <span className="location"><MapPin size={12} />{txn.location}</span>
                    <span>
                      <b className={`risk-number ${risk > 80 ? 'high-risk' : risk > 50 ? 'mid-risk' : 'low-risk'}`}>
                        {risk}
                      </b>
                    </span>
                    <span className={`txn-status ${statusClass}`}>
                      <i />{txn.status}
                    </span>
                  </motion.button>
                )
              })}
            </AnimatePresence>
          )}
        </div>
      </section>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '14px', color: '#677d91', fontSize: '11px', fontFamily: 'DM Mono, monospace' }}>
        <span>Showing {filteredItems.length} of {items.length} synthetic transactions</span>
        <span>Click any row to inspect explainability and execute actions</span>
      </div>

      <AnimatePresence>
        {selected && (
          <>
            <motion.div
              className="drawer-backdrop"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setSelected(null)}
            />
            <DetailDrawer txn={selected} close={() => setSelected(null)} onUpdateStatus={handleUpdateStatus} />
          </>
        )}
      </AnimatePresence>
    </div>
  )
}
