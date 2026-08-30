import { useEffect, useState } from 'react'
import { Play, Radar, ShieldCheck, Target } from 'lucide-react'
import { api, type Attack, type Simulation as SimulationRecord } from '../lib/api'

export default function Simulation() {
  const [attacks, setAttacks] = useState<Attack[]>([])
  const [attackId, setAttackId] = useState('')
  const [run, setRun] = useState<SimulationRecord | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  useEffect(() => { api.attacks().then((items) => { setAttacks(items); setAttackId(items[0]?.id ?? '') }).catch((reason: Error) => setError(reason.message)).finally(() => setLoading(false)) }, [])
  const launch = () => { setLoading(true); setError(null); api.startSimulation(attackId || undefined).then(setRun).catch((reason: Error) => setError(reason.message)).finally(() => setLoading(false)) }
  const selected = attacks.find((item) => item.id === attackId)
  return <div className="simulation-page"><div className="arena-heading"><div><p className="eyebrow">ATTACK SIMULATOR · Controlled synthetic run</p><h1>Adversarial Arena</h1><p className="subheading">Start a recorded run from an existing synthetic attack. Heuristic scores appear only when the selected attack supplies one; they are not measured probabilities.</p></div></div>
    <section className="arena-hero glass-card"><div className="arena-intro"><span className="arena-kicker">{run ? run.status : 'READY'}</span><h2>{run ? run.id : 'Choose a synthetic attack.'}</h2><p>{run ? `Created ${new Date(run.created_at).toLocaleString()}` : attacks.length ? 'The backend will create and persist the simulation run.' : 'Generate an attack in the Red Team Lab first, or create a scoreless run.'}</p><select value={attackId} onChange={(event) => setAttackId(event.target.value)}><option value="">No linked attack</option>{attacks.map((item) => <option key={item.id} value={item.id}>{item.id} · {item.name}</option>)}</select><button className="launch-button" disabled={loading} onClick={launch}><Play size={17} /> {loading ? 'LOADING…' : 'START SIMULATION'}</button></div><div className="arena-core"><div className="arena-versus"><span>RED TEAM</span><strong>VS</strong><span>BLUE TEAM</span></div><div className="arena-core-mark"><Radar size={22} /></div></div></section>
    {error && <div className="error-state" style={{ padding: 20 }}>{error}</div>}
    <div className="arena-grid"><section className="team-panel red-team-panel glass-card"><div className="team-title"><div className="team-icon red"><Target size={17} /></div><div><p className="eyebrow">Selected synthetic attack</p><h2>{selected?.name ?? 'None linked'}</h2></div></div><div className="team-metrics"><div><span>Accounts</span><strong>{selected?.accounts ?? 'Not evaluated'}</strong></div><div><span>Devices</span><strong>{selected?.devices ?? 'Not evaluated'}</strong></div><div><span>Transactions</span><strong>{selected?.transactions ?? 'Not evaluated'}</strong></div></div></section><section className="team-panel blue-team-panel glass-card"><div className="team-title"><div className="team-icon blue"><ShieldCheck size={17} /></div><div><p className="eyebrow">Stored result</p><h2>Heuristic detection score</h2></div></div><div className="team-metrics"><div><span>Score</span><strong>{run?.detection_score == null ? 'Not evaluated' : `${run.detection_score} / 100`}</strong></div><div><span>Stage</span><strong>{run?.stage ?? 'Not evaluated'}</strong></div><div><span>Status</span><strong>{run?.status ?? 'Not evaluated'}</strong></div></div></section></div>
  </div>
}
