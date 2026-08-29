import { useEffect, useState } from 'react'
import {
  Check,
  CircleDot,
  Database,
  Globe2,
  Lock,
  RefreshCw,
  Save,
  Server,
  ShieldCheck,
  Sliders,
  Terminal,
  Zap,
} from 'lucide-react'
import { api, type AuditEvent } from '../lib/api'

export default function Settings() {
  const [saved, setSaved] = useState(false)
  const [workspaceName, setWorkspaceName] = useState('EvoPay Security Lab')
  const [env, setEnv] = useState('Synthetic Demo Sandbox')
  const [offlineFallback, setOfflineFallback] = useState(true)
  const [allowThreshold, setAllowThreshold] = useState(30)
  const [stepUpThreshold, setStepUpThreshold] = useState(60)
  const [holdThreshold, setHoldThreshold] = useState(80)
  const [apiOnline, setApiOnline] = useState<boolean | null>(null)
  const [auditLogs, setAuditLogs] = useState<AuditEvent[]>([])

  useEffect(() => {
    api.dashboard()
      .then(() => setApiOnline(true))
      .catch(() => setApiOnline(false))
    api.audit().then(setAuditLogs).catch(console.error)
  }, [])

  const handleSave = () => {
    setSaved(true)
    setTimeout(() => setSaved(false), 2500)
  }

  return (
    <div className="data-page">
      <div className="data-page-heading" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: '24px' }}>
        <div>
          <p className="eyebrow">Workspace Configuration <span>•</span> System Preferences</p>
          <h1 style={{ margin: 0, fontSize: '32px', fontWeight: 500 }}>Settings</h1>
          <p className="subheading">Configure payment security policies, runtime connection parameters, and threat response thresholds.</p>
        </div>
        <button className="primary-button" onClick={handleSave}>
          <Save size={14} /> {saved ? 'Configuration Saved' : 'Save Changes'}
        </button>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px' }}>
        <section className="glass-card" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
            <div className="command-metric-icon cyan" style={{ margin: 0 }}><ShieldCheck size={16} /></div>
            <div>
              <h2 style={{ margin: 0, fontSize: '16px', fontWeight: 500 }}>Workspace Details</h2>
              <span style={{ fontSize: '11px', color: '#748b9f' }}>Environment and deployment context</span>
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
            <div>
              <label style={{ display: 'block', fontSize: '11px', color: '#889eb2', marginBottom: '6px', fontFamily: 'DM Mono, monospace' }}>
                WORKSPACE NAME
              </label>
              <input
                value={workspaceName}
                onChange={(e) => setWorkspaceName(e.target.value)}
                style={{ width: '100%', height: '36px', background: '#0b1d2e', border: '1px solid #1f374c', borderRadius: '5px', color: '#ecf3f8', padding: '0 12px', fontSize: '12px' }}
              />
            </div>

            <div>
              <label style={{ display: 'block', fontSize: '11px', color: '#889eb2', marginBottom: '6px', fontFamily: 'DM Mono, monospace' }}>
                ENVIRONMENT MODE
              </label>
              <select
                value={env}
                onChange={(e) => setEnv(e.target.value)}
                style={{ width: '100%', height: '36px', background: '#0b1d2e', border: '1px solid #1f374c', borderRadius: '5px', color: '#ecf3f8', padding: '0 12px', fontSize: '12px' }}
              >
                <option>Synthetic Demo Sandbox</option>
                <option>Staging Simulator</option>
                <option>Production Verification</option>
              </select>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '12px 0 0', borderTop: '1px solid #183042' }}>
              <div>
                <strong style={{ fontSize: '12px', display: 'block', color: '#d8e4ed' }}>Demo Fallback Mode</strong>
                <span style={{ fontSize: '10px', color: '#71889c' }}>Keep local demo state active if API is unreachable</span>
              </div>
              <button
                className={`secondary-button ${offlineFallback ? 'success-button' : ''}`}
                style={{ height: '30px', fontSize: '10px' }}
                onClick={() => setOfflineFallback((v) => !v)}
              >
                {offlineFallback ? 'Enabled' : 'Disabled'}
              </button>
            </div>
          </div>
        </section>

        <section className="glass-card" style={{ padding: '20px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
            <div className="command-metric-icon blue" style={{ margin: 0 }}><Server size={16} /></div>
            <div>
              <h2 style={{ margin: 0, fontSize: '16px', fontWeight: 500 }}>Runtime Status</h2>
              <span style={{ fontSize: '11px', color: '#748b9f' }}>FastAPI backend & SQLite database status</span>
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '10px 12px', background: '#0a1a2b', borderRadius: '6px', border: '1px solid #183044', fontSize: '11px' }}>
              <span style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#889eb2' }}>
                <Globe2 size={14} /> Backend API Endpoint
              </span>
              <strong style={{ color: '#57dcdb', fontFamily: 'DM Mono, monospace' }}>
                {import.meta.env.VITE_API_URL ?? 'http://127.0.0.1:8000/api'}
              </strong>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '10px 12px', background: '#0a1a2b', borderRadius: '6px', border: '1px solid #183044', fontSize: '11px' }}>
              <span style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#889eb2' }}>
                <Database size={14} /> Database Storage
              </span>
              <strong style={{ color: '#5ed596', fontFamily: 'DM Mono, monospace' }}>
                SQLite (backend/evopay.db)
              </strong>
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', padding: '10px 12px', background: '#0a1a2b', borderRadius: '6px', border: '1px solid #183044', fontSize: '11px' }}>
              <span style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#889eb2' }}>
                <CircleDot size={14} /> Health Status
              </span>
              <strong style={{ color: apiOnline === true ? '#5ed596' : apiOnline === false ? '#ef747b' : '#e4b258', fontFamily: 'DM Mono, monospace' }}>
                {apiOnline === true ? '● Online (Healthy)' : apiOnline === false ? '○ Offline' : 'Checking...'}
              </strong>
            </div>
          </div>
        </section>
      </div>

      <section className="glass-card" style={{ padding: '20px', marginBottom: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
          <div className="command-metric-icon amber" style={{ margin: 0 }}><Sliders size={16} /></div>
          <div>
            <h2 style={{ margin: 0, fontSize: '16px', fontWeight: 500 }}>Adaptive Risk Policy Thresholds</h2>
            <span style={{ fontSize: '11px', color: '#748b9f' }}>Define risk score boundary actions (0 to 100)</span>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '14px' }}>
          <div style={{ background: '#0c2226', padding: '14px', borderRadius: '6px', border: '1px solid #194644' }}>
            <span style={{ fontSize: '10px', color: '#61d697', fontFamily: 'DM Mono, monospace' }}>ALLOW ACTION</span>
            <strong style={{ display: 'block', fontSize: '20px', margin: '4px 0', color: '#f0f6fa' }}>0 – {allowThreshold}</strong>
            <small style={{ fontSize: '10px', color: '#7e96a4' }}>Seamless approval for normal transactions</small>
          </div>

          <div style={{ background: '#0d2836', padding: '14px', borderRadius: '6px', border: '1px solid #1f4f66' }}>
            <span style={{ fontSize: '10px', color: '#69cddd', fontFamily: 'DM Mono, monospace' }}>VERIFY ACTION</span>
            <strong style={{ display: 'block', fontSize: '20px', margin: '4px 0', color: '#f0f6fa' }}>{allowThreshold + 1} – {stepUpThreshold}</strong>
            <small style={{ fontSize: '10px', color: '#7e96a4' }}>Step-up MFA & biometric confirmation</small>
          </div>

          <div style={{ background: '#262216', padding: '14px', borderRadius: '6px', border: '1px solid #584a22' }}>
            <span style={{ fontSize: '10px', color: '#e4b258', fontFamily: 'DM Mono, monospace' }}>HOLD ACTION</span>
            <strong style={{ display: 'block', fontSize: '20px', margin: '4px 0', color: '#f0f6fa' }}>{stepUpThreshold + 1} – {holdThreshold}</strong>
            <small style={{ fontSize: '10px', color: '#7e96a4' }}>Temporary settlement hold for review</small>
          </div>

          <div style={{ background: '#2c1920', padding: '14px', borderRadius: '6px', border: '1px solid #622d37' }}>
            <span style={{ fontSize: '10px', color: '#ef747b', fontFamily: 'DM Mono, monospace' }}>BLOCK ACTION</span>
            <strong style={{ display: 'block', fontSize: '20px', margin: '4px 0', color: '#f0f6fa' }}>{holdThreshold + 1} – 100</strong>
            <small style={{ fontSize: '10px', color: '#7e96a4' }}>Autonomous block & incident triage</small>
          </div>
        </div>
      </section>

      <section className="glass-card" style={{ padding: '20px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
          <div>
            <p className="eyebrow">Audit & Compliance</p>
            <h2 style={{ margin: 0, fontSize: '16px', fontWeight: 500 }}>System Event Log</h2>
          </div>
          <span style={{ fontSize: '10px', color: '#688096', fontFamily: 'DM Mono, monospace' }}>
            {auditLogs.length} events recorded
          </span>
        </div>

        <div style={{ maxHeight: '260px', overflowY: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '11px', fontFamily: 'DM Mono, monospace' }}>
            <thead>
              <tr style={{ color: '#688096', borderBottom: '1px solid #1c3345', textAlign: 'left' }}>
                <th style={{ padding: '8px 12px' }}>Event Type</th>
                <th style={{ padding: '8px 12px' }}>Target Entity</th>
                <th style={{ padding: '8px 12px' }}>Details</th>
                <th style={{ padding: '8px 12px' }}>Timestamp</th>
              </tr>
            </thead>
            <tbody>
              {auditLogs.slice(0, 20).map((evt) => (
                <tr key={evt.id} style={{ borderBottom: '1px solid #132435', color: '#cad8e2' }}>
                  <td style={{ padding: '8px 12px', color: '#57dcdb' }}>{evt.event_type}</td>
                  <td style={{ padding: '8px 12px' }}>{evt.entity_id}</td>
                  <td style={{ padding: '8px 12px', maxWidth: '340px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{evt.details}</td>
                  <td style={{ padding: '8px 12px', color: '#667d91' }}>{evt.created_at}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  )
}
