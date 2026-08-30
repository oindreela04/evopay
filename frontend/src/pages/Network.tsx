import { useEffect, useMemo, useState } from 'react'
import { Link2, Network as NetworkIcon, RefreshCw, Search } from 'lucide-react'
import { api, type NetworkData } from '../lib/api'

export default function Network() {
  const [data, setData] = useState<NetworkData | null>(null)
  const [query, setQuery] = useState('')
  const [error, setError] = useState<string | null>(null)
  const load = () => { setError(null); api.network().then(setData).catch((reason: Error) => setError(reason.message)) }
  useEffect(load, [])
  const nodes = useMemo(() => (data?.nodes ?? []).filter((node) => `${node.id} ${node.name} ${node.type} ${node.city}`.toLowerCase().includes(query.toLowerCase())), [data, query])
  const ids = new Set(nodes.map((node) => node.id))
  const relationships = (data?.relationships ?? []).filter((edge) => ids.has(edge.from) || ids.has(edge.to))
  return <div className="network-page"><div className="network-heading"><div><p className="eyebrow">FRAUD NETWORK · Recorded synthetic entities</p><h1>Payment Network</h1><p className="subheading">Relationships are derived from stored transactions. EvoPay does not infer unrecorded accounts, IPs, clusters, or risk scores.</p></div><button className="network-reset" onClick={load}><RefreshCw size={14} /> Refresh</button></div>
    <div className="graph-toolbar glass-card"><div className="graph-search"><Search size={15} /><input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="Search recorded entities…" /></div></div>
    {error && <div className="error-state" style={{ padding: 22 }}>{error}</div>}
    {!data && !error && <div className="loading-state glass-card" style={{ padding: 22 }}>Loading relationship records</div>}
    {data && <div className="network-layout"><section className="graph-card glass-card" style={{ padding: 24 }}><div className="section-heading"><div><p className="eyebrow">Entities</p><h2>{nodes.length} recorded</h2></div><NetworkIcon size={17} /></div><div className="activity-list">{nodes.map((node) => <div className="activity-item" key={node.id}><div className="activity-icon cyan"><NetworkIcon size={15} /></div><div className="activity-copy"><strong>{node.name}</strong><span>{node.id} · {node.type}{node.city ? ` · ${node.city}` : ''}</span></div></div>)}</div>{!nodes.length && <div className="empty-state">No matching entities.</div>}</section><aside className="network-sidebar"><div className="filter-card glass-card"><div className="section-heading"><div><p className="eyebrow">Relationships</p><h2>{relationships.length} recorded</h2></div><Link2 size={15} /></div>{relationships.map((edge, index) => <div className="recent-attack" key={`${edge.from}-${edge.to}-${index}`}><strong>{edge.from}</strong><span>{edge.type}</span><strong>{edge.to}</strong></div>)}{!relationships.length && <div className="empty-state">No relationships have been recorded.</div>}</div></aside></div>}
  </div>
}
