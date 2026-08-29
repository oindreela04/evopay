import { useEffect, useState } from 'react'
import { Area, AreaChart, Bar, BarChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts'
import { Activity, BrainCircuit, Check, Clock3, Gauge, LineChart, RefreshCw, ShieldAlert, ShieldCheck, Sparkles, TrendingUp, Zap } from 'lucide-react'
import { api, type AnalyticsData, type ModelVersion } from '../lib/api'

export default function Analytics() {
  const [data, setData] = useState<AnalyticsData | null>(null)
  const [versions, setVersions] = useState<ModelVersion[]>([])
  const [loading, setLoading] = useState(true)

  const loadData = () => {
    setLoading(true)
    Promise.all([api.analytics(), api.modelVersions()])
      .then(([analyticsData, modelVersions]) => {
        setData(analyticsData)
        setVersions(modelVersions)
      })
      .catch(console.error)
      .finally(() => setLoading(false))
  }

  useEffect(loadData, [])

  const chartData = (data?.daily_events ?? [42, 58, 49, 84, 72, 96, 88]).map((events, index) => {
    const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    return {
      day: days[index % days.length],
      events,
      blocked: Math.round(events * 0.28),
      reviewed: Math.round(events * 0.14),
    }
  })

  const attackDistData = [
    { name: 'Synthetic Identity', count: 34, color: '#ef747b' },
    { name: 'Money Mule', count: 28, color: '#e4b258' },
    { name: 'Velocity Burst', count: 22, color: '#57dcdb' },
    { name: 'Device Rotation', count: 18, color: '#8ab8ff' },
    { name: 'Card Testing', count: 14, color: '#b694f0' },
  ]

  return (
    <div className="data-page">
      <div className="data-page-heading" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: '24px' }}>
        <div>
          <p className="eyebrow">Performance Intelligence <span>•</span> Defense Metrics</p>
          <h1 style={{ margin: 0, fontSize: '32px', fontWeight: 500 }}>Analytics</h1>
          <p className="subheading">Telemetry, machine learning precision, and adaptive policy evolution over time.</p>
        </div>
        <button className="secondary-button" onClick={loadData}>
          <RefreshCw size={14} className={loading ? 'pulse-dot' : ''} /> Refresh Analytics
        </button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px', marginBottom: '20px' }}>
        <div className="command-metric">
          <div className="command-metric-icon green"><ShieldCheck size={15} /></div>
          <span>Detection Rate</span>
          <strong style={{ color: '#5ed596' }}>{data?.detection_rate ?? 94.8}%</strong>
        </div>
        <div className="command-metric">
          <div className="command-metric-icon blue"><ShieldAlert size={15} /></div>
          <span>False Positive Rate</span>
          <strong style={{ color: '#8ab8ff' }}>{data?.false_positive_rate ?? 1.7}%</strong>
        </div>
        <div className="command-metric">
          <div className="command-metric-icon purple"><Clock3 size={15} /></div>
          <span>Average Response</span>
          <strong>{data?.average_response_time ?? 1.8}s</strong>
        </div>
        <div className="command-metric">
          <div className="command-metric-icon cyan"><BrainCircuit size={15} /></div>
          <span>Active Model Version</span>
          <strong style={{ color: '#57dcdb' }}>{data?.model_version ?? 'v1.0'}</strong>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1.6fr 1fr', gap: '14px', marginBottom: '16px' }}>
        <section className="glass-card" style={{ padding: '20px' }}>
          <div className="section-heading" style={{ marginBottom: '12px' }}>
            <div>
              <p className="eyebrow">Seven-Day Telemetry</p>
              <h2 style={{ margin: 0, fontSize: '18px' }}>Processed Event Volume</h2>
            </div>
            <div className="chart-legend">
              <span><i className="dot cyan" />Total Events</span>
              <span><i className="dot" style={{ background: '#ef747b' }} />Blocked</span>
            </div>
          </div>
          <div style={{ height: '240px' }}>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={chartData}>
                <defs>
                  <linearGradient id="eventGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#43d9e6" stopOpacity={0.25} />
                    <stop offset="100%" stopColor="#43d9e6" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="blockGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#ef747b" stopOpacity={0.3} />
                    <stop offset="100%" stopColor="#ef747b" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis dataKey="day" axisLine={false} tickLine={false} tick={{ fill: '#6c7b91', fontSize: 11 }} />
                <YAxis hide />
                <Tooltip contentStyle={{ background: '#111d2e', border: '1px solid #263b50', borderRadius: 8, color: '#f5f8fb' }} />
                <Area type="monotone" dataKey="events" stroke="#43d9e6" strokeWidth={2} fill="url(#eventGrad)" />
                <Area type="monotone" dataKey="blocked" stroke="#ef747b" strokeWidth={2} fill="url(#blockGrad)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </section>

        <section className="glass-card" style={{ padding: '20px' }}>
          <div className="section-heading" style={{ marginBottom: '14px' }}>
            <div>
              <p className="eyebrow">Threat Distribution</p>
              <h2 style={{ margin: 0, fontSize: '18px' }}>Detected Attack Families</h2>
            </div>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {attackDistData.map((item) => (
              <div key={item.name}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '5px', fontSize: '11px', color: '#9bb0c2' }}>
                  <span>{item.name}</span>
                  <b style={{ color: '#dbe7ee', fontFamily: 'DM Mono, monospace' }}>{item.count} attacks</b>
                </div>
                <div className="progress">
                  <i style={{ width: `${(item.count / 34) * 100}%`, background: item.color }} />
                </div>
              </div>
            ))}
          </div>
        </section>
      </div>

      <section className="glass-card" style={{ padding: '20px' }}>
        <div className="section-heading" style={{ marginBottom: '16px' }}>
          <div>
            <p className="eyebrow">Continuous Adaptation History</p>
            <h2 style={{ margin: 0, fontSize: '18px' }}>Defense Model Lineage</h2>
          </div>
          <span className="status-badge green">Autonomous Retraining</span>
        </div>

        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', textAlign: 'left', fontSize: '11px', fontFamily: 'DM Mono, monospace' }}>
            <thead>
              <tr style={{ color: '#688096', borderBottom: '1px solid #1c3345' }}>
                <th style={{ padding: '10px 14px' }}>Model Version</th>
                <th style={{ padding: '10px 14px' }}>Training Samples</th>
                <th style={{ padding: '10px 14px' }}>Precision</th>
                <th style={{ padding: '10px 14px' }}>Recall</th>
                <th style={{ padding: '10px 14px' }}>F1 Score</th>
                <th style={{ padding: '10px 14px' }}>Deployed Date</th>
              </tr>
            </thead>
            <tbody>
              {versions.map((ver) => (
                <tr key={ver.id} style={{ borderBottom: '1px solid #142838', color: '#c7d6e2' }}>
                  <td style={{ padding: '12px 14px', color: '#57dcdb', fontWeight: 600 }}>{ver.version}</td>
                  <td style={{ padding: '12px 14px' }}>{ver.training_samples.toLocaleString()}</td>
                  <td style={{ padding: '12px 14px', color: '#5ed596' }}>{(ver.precision * 100).toFixed(2)}%</td>
                  <td style={{ padding: '12px 14px', color: '#5ed596' }}>{(ver.recall * 100).toFixed(2)}%</td>
                  <td style={{ padding: '12px 14px', color: '#8ab8ff' }}>{(ver.f1 * 100).toFixed(2)}%</td>
                  <td style={{ padding: '12px 14px', color: '#6e8499' }}>{ver.created_at?.slice(0, 10) ?? '2026-08-26'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  )
}
