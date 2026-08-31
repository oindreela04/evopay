from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
import json
import sqlite3

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware

import os

try:
    from database import create_db_and_tables, get_connection
    from schemas import (
        ActionRequest,
        AuthRequest,
        AnalyticsResponse,
        AttackEvolveRequest,
        AttackGenerateRequest,
        AttackResponse,
        AuditEventResponse,
        DashboardResponse,
        DefenseAdaptRequest,
        DefenseAdaptResponse,
        HealthResponse,
        IncidentActionRequest,
        IncidentResponse,
        InvestigationRequest,
        InvestigatorResponse,
        ModelVersionResponse,
        NetworkResponse,
        RiskAnalysisResponse,
        SimulationResponse,
        SimulationStartRequest,
        ThreatPatternRequest,
        TransactionResponse,
        UserResponse,
    )
    from services.risk_engine import analyze_transaction
    from services.attack_engine import attack_type_parameters, evolve_attack as evolve_attack_model, generate_attack as generate_attack_model
    from services.investigator import investigate_transaction
except ImportError:
    from database import create_db_and_tables, get_connection
    from schemas import (
        ActionRequest,
        AuthRequest,
        AnalyticsResponse,
        AttackEvolveRequest,
        AttackGenerateRequest,
        AttackResponse,
        AuditEventResponse,
        DashboardResponse,
        DefenseAdaptRequest,
        DefenseAdaptResponse,
        HealthResponse,
        IncidentActionRequest,
        IncidentResponse,
        InvestigationRequest,
        InvestigatorResponse,
        ModelVersionResponse,
        NetworkResponse,
        RiskAnalysisResponse,
        SimulationResponse,
        SimulationStartRequest,
        ThreatPatternRequest,
        TransactionResponse,
        UserResponse,
    )
    from services.risk_engine import analyze_transaction
    from services.attack_engine import attack_type_parameters, evolve_attack as evolve_attack_model, generate_attack as generate_attack_model
    from services.investigator import investigate_transaction

from auth import (
    PASSWORD_HASHER, SESSION_COOKIE, clear_session_cookies, create_session, current_user,
    enforce_rate_limit, normalize_email, public_user, token_hash, validate_password, verify_password,
)

app = FastAPI(title="EvoPay AI API", version="0.2.0")

raw_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000")
allowed_origins = [origin.strip() for origin in raw_origins.split(",") if origin.strip() and origin.strip() != "*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def now() -> str:
    return datetime.now(timezone.utc).isoformat()

def rows(query: str, params: tuple = ()) -> list[dict]:
    with get_connection() as connection:
        return [dict(row) for row in connection.execute(query, params).fetchall()]

def row(query: str, params: tuple = ()) -> dict | None:
    result = rows(query, params)
    return result[0] if result else None

def audit(connection: sqlite3.Connection, user_id: str, event_type: str, entity_id: str, details: dict) -> None:
    connection.execute("INSERT INTO audit_events (event_type, entity_id, details, user_id) VALUES (?, ?, ?, ?)", (event_type, entity_id, json.dumps(details), user_id))

@app.on_event("startup")
def on_startup() -> None:
    create_db_and_tables()

@app.get("/api/health", response_model=HealthResponse)
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "evopay-ai"}

@app.post("/api/auth/signup", response_model=UserResponse, status_code=201)
def signup(payload: AuthRequest, request: Request, response: Response) -> dict:
    email = normalize_email(payload.email)
    validate_password(payload.password)
    display_name = (payload.display_name or email.split("@", 1)[0]).strip()
    if not 2 <= len(display_name) <= 80:
        raise HTTPException(422, "Display name must be between 2 and 80 characters")
    enforce_rate_limit(f"signup:{request.client.host if request.client else 'unknown'}:{email}", 4, 300)
    user_id = str(uuid4())
    with get_connection() as connection:
        try:
            connection.execute("INSERT INTO users (id, email, display_name, password_hash, created_at) VALUES (?, ?, ?, ?, ?)", (user_id, email, display_name, PASSWORD_HASHER.hash(payload.password), now()))
        except sqlite3.IntegrityError as error:
            raise HTTPException(409, "An account with this email already exists") from error
        create_session(connection, user_id, response)
        connection.commit()
    return {"id": user_id, "email": email, "display_name": display_name}

@app.post("/api/auth/login", response_model=UserResponse)
def login(payload: AuthRequest, request: Request, response: Response) -> dict:
    email = normalize_email(payload.email)
    enforce_rate_limit(f"login:{request.client.host if request.client else 'unknown'}:{email}", 5, 60)
    with get_connection() as connection:
        user = connection.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        if not user or not verify_password(user["password_hash"], payload.password):
            raise HTTPException(401, "Email or password is incorrect")
        create_session(connection, user["id"], response)
        connection.commit()
        return public_user(user)

@app.get("/api/auth/me", response_model=UserResponse)
def me(user: dict = Depends(current_user)) -> dict:
    return user

@app.post("/api/auth/logout", status_code=204)
def logout(request: Request, response: Response, user: dict = Depends(current_user)) -> Response:
    session_token = request.cookies.get(SESSION_COOKIE)
    with get_connection() as connection:
        connection.execute("DELETE FROM user_sessions WHERE token_hash = ? AND user_id = ?", (token_hash(session_token or ""), user["id"]))
        connection.commit()
    clear_session_cookies(response)
    response.status_code = 204
    return response

@app.get("/api/dashboard", response_model=DashboardResponse)
def dashboard(user: dict = Depends(current_user)) -> dict:
    uid = user["id"]
    active_threats = len(rows("SELECT 1 FROM incidents WHERE user_id = ? AND status != 'RESOLVED'", (uid,)))
    transactions_total = row("SELECT COUNT(*) AS count FROM transactions WHERE user_id = ?", (uid,))
    attacks_sim = row("SELECT COUNT(*) AS count FROM attacks WHERE user_id = ?", (uid,))
    detection = row("SELECT AVG(detection_probability) AS value FROM attacks WHERE user_id = ?", (uid,))
    return {
        "metrics": {
            "transactions_monitored": transactions_total["count"] if transactions_total else 0,
            "active_threats": active_threats,
            "attacks_simulated": attacks_sim["count"] if attacks_sim else 0,
            "mean_detection_score": round(detection["value"], 1) if detection and detection["value"] is not None else None,
            "false_positive_rate": None,
            "average_detection_time": None,
        },
        "transactions": rows("SELECT * FROM transactions WHERE user_id = ? ORDER BY created_at DESC", (uid,)),
        "incidents": rows("SELECT * FROM incidents WHERE user_id = ? ORDER BY created_at DESC", (uid,)),
    }

@app.get("/api/transactions", response_model=list[TransactionResponse])
def transactions(limit: int = 50, offset: int = 0, user: dict = Depends(current_user)) -> list[dict]:
    limit = max(1, min(limit, 200))
    offset = max(0, offset)
    return [{**item, "synthetic": True} for item in rows("SELECT * FROM transactions WHERE user_id = ? ORDER BY created_at DESC LIMIT ? OFFSET ?", (user["id"], limit, offset))]

@app.get("/api/transactions/{transaction_id}", response_model=TransactionResponse)
def transaction(transaction_id: str, user: dict = Depends(current_user)) -> dict:
    result = row("SELECT * FROM transactions WHERE id = ? AND user_id = ?", (transaction_id, user["id"]))
    if not result:
        raise HTTPException(404, "Transaction not found")
    return {**result, "synthetic": True}

@app.get("/api/transactions/{transaction_id}/risk", response_model=RiskAnalysisResponse)
def transaction_risk(transaction_id: str, user: dict = Depends(current_user)) -> dict:
    result = row("SELECT * FROM transactions WHERE id = ? AND user_id = ?", (transaction_id, user["id"]))
    if not result:
        raise HTTPException(404, "Transaction not found")
    return analyze_transaction(result)

@app.post("/api/transactions/{transaction_id}/analyze", response_model=RiskAnalysisResponse)
def transaction_analyze(transaction_id: str, user: dict = Depends(current_user)) -> dict:
    result = row("SELECT * FROM transactions WHERE id = ? AND user_id = ?", (transaction_id, user["id"]))
    if not result:
        raise HTTPException(404, "Transaction not found")
    analysis = analyze_transaction(result)
    with get_connection() as connection:
        audit(connection, user["id"], "transaction_analyzed", transaction_id, analysis)
        if analysis["risk_score"] >= 81:
            incident_id = f"INC-{uuid4().hex[:6].upper()}"
            connection.execute(
                "INSERT OR IGNORE INTO incidents (id, title, severity, status, created_at, transaction_id, risk_score, reasons, user_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (incident_id, "High-risk transaction detected", analysis["classification"], "OPEN", now(), transaction_id, analysis["risk_score"], json.dumps(analysis["reasons"]), user["id"])
            )
            audit(connection, user["id"], "incident_created", incident_id, {"transaction_id": transaction_id, "risk_score": analysis["risk_score"]})
        connection.commit()
    return analysis

@app.post("/api/transactions/{transaction_id}/action")
def transaction_action(transaction_id: str, payload: ActionRequest, user: dict = Depends(current_user)) -> dict:
    allowed = {"ALLOW", "VERIFY", "HOLD", "BLOCK", "ALLOWED", "BLOCKED"}
    action = payload.action.upper()
    if action not in allowed:
        raise HTTPException(400, "Action must be ALLOW, VERIFY, HOLD, or BLOCK")
    status = {"ALLOW": "ALLOWED", "BLOCK": "BLOCKED"}.get(action, action)
    with get_connection() as connection:
        if not connection.execute("SELECT 1 FROM transactions WHERE id = ? AND user_id = ?", (transaction_id, user["id"])).fetchone():
            raise HTTPException(404, "Transaction not found")
        connection.execute("UPDATE transactions SET status = ? WHERE id = ? AND user_id = ?", (status, transaction_id, user["id"]))
        audit(connection, user["id"], "transaction_action", transaction_id, {"action": action, "status": status})
        connection.commit()
    return {"transaction_id": transaction_id, "status": status}

@app.get("/api/attacks", response_model=list[AttackResponse])
def attacks(user: dict = Depends(current_user)) -> list[dict]:
    response = []
    for item in rows("SELECT * FROM attacks WHERE user_id = ? ORDER BY created_at DESC", (user["id"],)):
        detection_score = item.pop("detection_probability", None)
        response.append({**item, "detection_score": detection_score, "synthetic": True})
    return response

@app.post("/api/attacks/generate", response_model=AttackResponse)
def generate_attack(payload: AttackGenerateRequest, user: dict = Depends(current_user)) -> dict:
    attack_id = f"EV-{uuid4().hex[:4].upper()}"
    attack_type = payload.attack_type or payload.strategy
    try:
        generated = generate_attack_model(attack_type, payload.generation)
    except ValueError as error:
        raise HTTPException(400, str(error)) from error
    merchants = max(1, round(int(generated["accounts"]) / 2))
    transaction_count = max(1, round(int(generated["accounts"]) * float(generated["transaction_velocity"])))
    attack = (attack_id, payload.strategy, "CRITICAL", "UNDER SIMULATION", generated["accounts"], generated["devices"], merchants, transaction_count, now(), generated["attack_type"], json.dumps(generated), generated["attack_score"], generated["detection_score"], int(generated["evasion_success"]), generated["generation"])
    created_at = attack[8]
    with get_connection() as connection:
        connection.execute("INSERT INTO attacks (id, name, severity, status, accounts, devices, merchants, transactions, created_at, attack_type, parameters, attack_score, detection_probability, evasion_success, generation, user_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", (*attack, user["id"]))
        customer_ids = [f"SYN-C-{attack_id[3:]}-{index + 1:03d}" for index in range(int(generated["accounts"]))]
        device_ids = [f"SYN-D-{attack_id[3:]}-{index + 1:03d}" for index in range(int(generated["devices"]))]
        merchant_ids = [f"SYN-M-{attack_id[3:]}-{index + 1:03d}" for index in range(merchants)]
        connection.executemany("INSERT INTO customers (id, name, city, user_id) VALUES (?, ?, ?, ?)", [(item, f"Synthetic customer {index + 1}", "Simulation Lab", user["id"]) for index, item in enumerate(customer_ids)])
        connection.executemany("INSERT INTO devices (id, platform, risk_score, user_id) VALUES (?, ?, ?, ?)", [(item, "Simulated device", int(generated["attack_score"]), user["id"]) for item in device_ids])
        connection.executemany("INSERT INTO merchants (id, name, city, user_id) VALUES (?, ?, ?, ?)", [(item, f"Synthetic merchant {index + 1}", "Simulation Lab", user["id"]) for index, item in enumerate(merchant_ids)])
        risk_score = int(generated["attack_score"])
        classification = analyze_transaction({"risk_score": risk_score})["classification"]
        status = {"LOW": "ALLOWED", "MEDIUM": "VERIFY", "HIGH": "HOLD", "CRITICAL": "BLOCKED"}[classification]
        connection.executemany("INSERT INTO transactions (id, customer_id, merchant_id, amount, location, payment_method, risk_score, status, device_id, created_at, user_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", [
            (f"SYN-TXN-{attack_id[3:]}-{index + 1:04d}", customer_ids[index % len(customer_ids)], merchant_ids[index % len(merchant_ids)], 1000 + index * 125, "Simulation Lab", "SIMULATED", risk_score, status, device_ids[index % len(device_ids)], created_at, user["id"])
            for index in range(transaction_count)
        ])
        audit(connection, user["id"], "attack_generated", attack_id, generated)
        connection.commit()
    return {"id": attack_id, "name": payload.strategy, "status": "UNDER SIMULATION", "severity": "CRITICAL", "merchants": merchants, "transactions": transaction_count, **generated, "created_at": attack[8], "synthetic": True}

@app.post("/api/attacks/evolve", response_model=AttackResponse)
def evolve_attack(payload: AttackEvolveRequest, user: dict = Depends(current_user)) -> dict:
    current = row("SELECT * FROM attacks WHERE id = ? AND user_id = ?", (payload.attack_id, user["id"]))
    if not current:
        raise HTTPException(404, "Attack not found")
    try:
        attack_type = current.get("attack_type", "composite_attack")
        parameters = attack_type_parameters(attack_type)
        parameters.update(json.loads(current.get("parameters", "{}")))
        parameters.pop("detection_probability", None)
        evolved_data = evolve_attack_model({"attack_type": attack_type, "generation": current.get("generation", 1), **parameters, "attack_score": current.get("attack_score", 0), "detection_score": current.get("detection_probability", 0), "evasion_success": bool(current.get("evasion_success", 0))})
    except (ValueError, json.JSONDecodeError, TypeError, KeyError) as error:
        raise HTTPException(400, "Stored attack parameters are invalid") from error
    evolved = f"{current['name']} + Device Rotation + Mule Network"
    with get_connection() as connection:
        connection.execute("UPDATE attacks SET name = ?, status = ?, parameters = ?, accounts = ?, devices = ?, attack_score = ?, detection_probability = ?, evasion_success = ?, generation = ? WHERE id = ? AND user_id = ?", (evolved, "EVOLVED", json.dumps(evolved_data), evolved_data["accounts"], evolved_data["devices"], evolved_data["attack_score"], evolved_data["detection_score"], int(evolved_data["evasion_success"]), evolved_data["generation"], payload.attack_id, user["id"]))
        if evolved_data["evasion_success"]:
            connection.execute("INSERT INTO threat_patterns (name, description, severity, user_id) VALUES (?, ?, ?, ?)", ("DEFENSE BLIND SPOT", f"Evasion in generation {evolved_data['generation']} of {evolved_data['attack_type']}", "CRITICAL", user["id"]))
        audit(connection, user["id"], "attack_evolved", payload.attack_id, evolved_data)
        connection.commit()
    current.pop("detection_probability", None)
    current.update({"name": evolved, "status": "EVOLVED", **evolved_data, "synthetic": True})
    return current

@app.get("/api/network", response_model=NetworkResponse)
def network(user: dict = Depends(current_user)) -> dict:
    relationships = rows("""
        SELECT customer_id AS 'from', device_id AS 'to', 'uses' AS type FROM transactions WHERE user_id = ?
        UNION SELECT device_id AS 'from', merchant_id AS 'to', 'connects' AS type FROM transactions WHERE user_id = ?
        UNION SELECT customer_id AS 'from', merchant_id AS 'to', 'pays' AS type FROM transactions WHERE user_id = ?
    """, (user["id"], user["id"], user["id"]))
    return {
        "nodes": rows("SELECT id, name, city, 'Customer' AS type FROM customers WHERE user_id = ? UNION ALL SELECT id, name, city, 'Merchant' AS type FROM merchants WHERE user_id = ? UNION ALL SELECT id, platform AS name, '' AS city, 'Device' AS type FROM devices WHERE user_id = ?", (user["id"], user["id"], user["id"])),
        "relationships": relationships,
    }

@app.post("/api/simulation/start", response_model=SimulationResponse)
def start_simulation(payload: SimulationStartRequest, user: dict = Depends(current_user)) -> dict:
    simulation_id = f"SIM-{uuid4().hex[:8].upper()}"
    attack = row("SELECT detection_probability FROM attacks WHERE id = ? AND user_id = ?", (payload.attack_id, user["id"])) if payload.attack_id else None
    if payload.attack_id and not attack:
        raise HTTPException(404, "Attack not found")
    detection_score = float(attack["detection_probability"]) if attack and attack["detection_probability"] is not None else None
    result = {"id": simulation_id, "status": "RUNNING", "stage": 1, "detection_score": detection_score, "created_at": now(), "attack_id": payload.attack_id}
    with get_connection() as connection:
        connection.execute("INSERT INTO simulation_runs (id, status, stage, detection_score, created_at, user_id, attack_id) VALUES (?, ?, ?, ?, ?, ?, ?)", (simulation_id, "RUNNING", 1, detection_score, result["created_at"], user["id"], payload.attack_id))
        audit(connection, user["id"], "simulation_started", simulation_id, {"attack_id": payload.attack_id})
        connection.commit()
    return result

@app.get("/api/simulation/{simulation_id}", response_model=SimulationResponse)
def simulation(simulation_id: str, user: dict = Depends(current_user)) -> dict:
    result = row("SELECT * FROM simulation_runs WHERE id = ? AND user_id = ?", (simulation_id, user["id"]))
    if not result:
        raise HTTPException(404, "Simulation not found")
    return result

@app.get("/api/incidents", response_model=list[IncidentResponse])
def incidents(limit: int = 50, offset: int = 0, user: dict = Depends(current_user)) -> list[dict]:
    return [{**item, "synthetic": True} for item in rows("SELECT * FROM incidents WHERE user_id = ? ORDER BY created_at DESC LIMIT ? OFFSET ?", (user["id"], max(1, min(limit, 200)), max(0, offset)))]

@app.get("/api/audit", response_model=list[AuditEventResponse])
def audit_events(limit: int = 100, user: dict = Depends(current_user)) -> list[dict]:
    return rows("SELECT * FROM audit_events WHERE user_id = ? ORDER BY created_at DESC LIMIT ?", (user["id"], max(1, min(limit, 500))))

@app.post("/api/incidents/{incident_id}/action")
def incident_action(incident_id: str, payload: IncidentActionRequest, user: dict = Depends(current_user)) -> dict:
    status = payload.status.upper()
    if status not in {"OPEN", "INVESTIGATING", "CONTAINED", "RESOLVED"}:
        raise HTTPException(400, "Invalid incident status")
    with get_connection() as connection:
        if not connection.execute("SELECT 1 FROM incidents WHERE id = ? AND user_id = ?", (incident_id, user["id"])).fetchone():
            raise HTTPException(404, "Incident not found")
        connection.execute("UPDATE incidents SET status = ? WHERE id = ? AND user_id = ?", (status, incident_id, user["id"]))
        audit(connection, user["id"], "incident_status_changed", incident_id, {"status": status})
        connection.commit()
    return {"id": incident_id, "status": status}

@app.get("/api/analytics", response_model=AnalyticsResponse)
def analytics(user: dict = Depends(current_user)) -> dict:
    uid = user["id"]
    latest_version = row("SELECT version FROM model_versions WHERE user_id = ? ORDER BY id DESC LIMIT 1", (uid,))
    detection = row("SELECT AVG(detection_probability) AS value FROM attacks WHERE user_id = ?", (uid,))
    daily = rows("""
        SELECT day, SUM(total) AS count FROM (
            SELECT substr(created_at, 1, 10) AS day, COUNT(*) AS total FROM transactions WHERE user_id = ? GROUP BY day
            UNION ALL SELECT substr(created_at, 1, 10), COUNT(*) FROM attacks WHERE user_id = ? GROUP BY substr(created_at, 1, 10)
            UNION ALL SELECT substr(created_at, 1, 10), COUNT(*) FROM incidents WHERE user_id = ? GROUP BY substr(created_at, 1, 10)
        ) GROUP BY day ORDER BY day
    """, (uid, uid, uid))
    return {
        "mean_detection_score": round(detection["value"], 1) if detection and detection["value"] is not None else None,
        "false_positive_rate": None,
        "average_response_time": None,
        "daily_events": daily,
        "model_version": latest_version["version"] if latest_version else None,
    }

@app.get("/api/model-versions", response_model=list[ModelVersionResponse])
def model_versions(user: dict = Depends(current_user)) -> list[dict]:
    return rows("SELECT * FROM model_versions WHERE user_id = ? ORDER BY id DESC", (user["id"],))

@app.get("/api/threat-library")
def threat_library(user: dict = Depends(current_user)) -> list[dict]:
    return rows("SELECT * FROM threat_patterns WHERE user_id = ? ORDER BY id", (user["id"],))

@app.post("/api/threat-library")
def add_threat_pattern(payload: ThreatPatternRequest, user: dict = Depends(current_user)) -> dict:
    with get_connection() as connection:
        cursor = connection.execute("INSERT INTO threat_patterns (name, description, severity, user_id) VALUES (?, ?, ?, ?)", (payload.name, payload.description, payload.severity.upper(), user["id"]))
        connection.commit()
        return row("SELECT * FROM threat_patterns WHERE id = ? AND user_id = ?", (cursor.lastrowid, user["id"])) or {}

@app.post("/api/investigate")
def investigate(payload: InvestigationRequest, user: dict = Depends(current_user)) -> dict:
    transaction = payload.transaction
    if transaction is None and payload.transaction_id:
        transaction = row("SELECT * FROM transactions WHERE id = ? AND user_id = ?", (payload.transaction_id, user["id"]))
    if transaction is None:
        raise HTTPException(400, "Provide transaction_id or structured transaction data")
    network = payload.network or {}
    report = investigate_transaction(transaction, network)
    entity_id = payload.entity_id or payload.transaction_id or str(transaction.get("id", "unknown"))
    with get_connection() as connection:
        audit(connection, user["id"], "investigation_opened", entity_id, {"notes": payload.notes, "risk_score": report["risk_score"], "recommended_action": report["recommended_action"]})
        connection.commit()
    return {"status": "opened", "entity_id": entity_id, "notes": payload.notes, "investigation": report}

@app.post("/api/defense/adapt", response_model=DefenseAdaptResponse)
def adapt_defense(payload: DefenseAdaptRequest, user: dict = Depends(current_user)) -> dict:
    before = row("SELECT detection_probability FROM attacks WHERE user_id = ? ORDER BY created_at DESC LIMIT 1", (user["id"],))
    before_score = round(float(before["detection_probability"]), 1) if before and before["detection_probability"] is not None else None
    with get_connection() as connection:
        connection.execute("INSERT INTO threat_patterns (name, description, severity, user_id) VALUES (?, ?, ?, ?)", (payload.pattern, "Observed synthetic pattern added to defensive policy", "CRITICAL", user["id"]))
        audit(connection, user["id"], "defense_pattern_recorded", payload.pattern, {"before_detection_score": before_score, "evaluation_required": True})
        connection.commit()
    return {"before_detection_score": before_score, "after_detection_score": None, "model_version": None, "pattern": payload.pattern}

