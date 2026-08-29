from pathlib import Path
import sqlite3
from typing import Iterator

DATABASE_PATH = Path(__file__).parent / "evopay.db"


def get_connection() -> sqlite3.Connection:
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def connection_scope() -> Iterator[sqlite3.Connection]:
    connection = get_connection()
    try:
        yield connection
    finally:
        connection.close()


def create_db_and_tables() -> None:
    with get_connection() as connection:
        connection.executescript("""
        CREATE TABLE IF NOT EXISTS customers (id TEXT PRIMARY KEY, name TEXT NOT NULL, city TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS merchants (id TEXT PRIMARY KEY, name TEXT NOT NULL, city TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS devices (id TEXT PRIMARY KEY, platform TEXT NOT NULL, risk_score INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS transactions (
            id TEXT PRIMARY KEY, customer_id TEXT NOT NULL, merchant_id TEXT NOT NULL, amount INTEGER NOT NULL,
            location TEXT NOT NULL, payment_method TEXT NOT NULL, risk_score INTEGER NOT NULL,
            status TEXT NOT NULL, device_id TEXT NOT NULL, created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS attacks (
            id TEXT PRIMARY KEY, name TEXT NOT NULL, severity TEXT NOT NULL, status TEXT NOT NULL,
            accounts INTEGER NOT NULL, devices INTEGER NOT NULL, merchants INTEGER NOT NULL,
            transactions INTEGER NOT NULL, created_at TEXT NOT NULL, attack_type TEXT DEFAULT 'composite_attack',
            parameters TEXT DEFAULT '{}', attack_score INTEGER DEFAULT 0, detection_probability INTEGER DEFAULT 0,
            evasion_success INTEGER DEFAULT 0, generation INTEGER DEFAULT 1
        );
        CREATE TABLE IF NOT EXISTS attack_generations (id INTEGER PRIMARY KEY AUTOINCREMENT, attack_id TEXT NOT NULL, generation INTEGER NOT NULL, parameters TEXT NOT NULL, attack_realism REAL NOT NULL, financial_impact REAL NOT NULL, detection_probability REAL NOT NULL, evasion_score REAL NOT NULL, created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS incidents (id TEXT PRIMARY KEY, title TEXT NOT NULL, severity TEXT NOT NULL, status TEXT NOT NULL, created_at TEXT NOT NULL, transaction_id TEXT, attack_id TEXT, risk_score INTEGER, reasons TEXT DEFAULT '[]');
        CREATE TABLE IF NOT EXISTS threat_patterns (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, description TEXT NOT NULL, severity TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS simulation_runs (id TEXT PRIMARY KEY, status TEXT NOT NULL, stage INTEGER NOT NULL, detection_score REAL NOT NULL, created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS model_versions (id INTEGER PRIMARY KEY AUTOINCREMENT, version TEXT NOT NULL, training_samples INTEGER NOT NULL, precision REAL NOT NULL, recall REAL NOT NULL, f1 REAL NOT NULL, created_at TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS audit_events (id INTEGER PRIMARY KEY AUTOINCREMENT, event_type TEXT NOT NULL, entity_id TEXT NOT NULL, details TEXT NOT NULL, created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS system_events (id INTEGER PRIMARY KEY AUTOINCREMENT, event_type TEXT NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);
        """)
        attack_columns = {column[1] for column in connection.execute("PRAGMA table_info(attacks)").fetchall()}
        for column, definition in {
            "attack_type": "TEXT DEFAULT 'composite_attack'", "parameters": "TEXT DEFAULT '{}'",
            "attack_score": "INTEGER DEFAULT 0", "detection_probability": "INTEGER DEFAULT 0",
            "evasion_success": "INTEGER DEFAULT 0", "generation": "INTEGER DEFAULT 1",
        }.items():
            if column not in attack_columns:
                connection.execute(f"ALTER TABLE attacks ADD COLUMN {column} {definition}")
        incident_columns = {column[1] for column in connection.execute("PRAGMA table_info(incidents)").fetchall()}
        for column, definition in {"transaction_id": "TEXT", "attack_id": "TEXT", "risk_score": "INTEGER", "reasons": "TEXT DEFAULT '[]'"}.items():
            if column not in incident_columns:
                connection.execute(f"ALTER TABLE incidents ADD COLUMN {column} {definition}")
        seed_database(connection)
        connection.commit()


def seed_database(connection: sqlite3.Connection) -> None:
    if connection.execute("SELECT COUNT(*) FROM customers").fetchone()[0] == 0:
        connection.executemany("INSERT INTO customers VALUES (?, ?, ?)", [("C-A81F", "Customer #A81F", "Kolkata"), ("C-C44B", "Customer #C44B", "Mumbai"), ("C-D90E", "Customer #D90E", "Delhi"), ("C-F302", "Customer #F302", "Bengaluru"), ("C-B73C", "Customer #B73C", "Hyderabad")])
    if connection.execute("SELECT COUNT(*) FROM merchants").fetchone()[0] == 0:
        connection.executemany("INSERT INTO merchants VALUES (?, ?, ?)", [("M-M921", "Merchant #M921", "Kolkata"), ("M-M104", "Merchant #M104", "Mumbai"), ("M-M772", "Merchant #M772", "Delhi"), ("M-M318", "Merchant #M318", "Bengaluru"), ("M-M442", "Merchant #M442", "Chennai")])
    if connection.execute("SELECT COUNT(*) FROM devices").fetchone()[0] == 0:
        connection.executemany("INSERT INTO devices VALUES (?, ?, ?)", [("D-X28", "Android", 96), ("D-A11", "iOS", 31), ("D-Q41", "Android", 68), ("D-P07", "Web", 22)])
    if connection.execute("SELECT COUNT(*) FROM transactions").fetchone()[0] == 0:
        connection.executemany("INSERT INTO transactions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", [
            ("TXN-84921", "C-A81F", "M-M921", 12840, "Kolkata", "UPI", 94, "BLOCKED", "D-X28", "2026-08-26T16:42:09Z"),
            ("TXN-84920", "C-C44B", "M-M104", 2499, "Mumbai", "Card", 71, "VERIFY", "D-Q41", "2026-08-26T16:42:04Z"),
            ("TXN-84919", "C-D90E", "M-M772", 48200, "Delhi", "Net Banking", 89, "BLOCKED", "D-X28", "2026-08-26T16:41:58Z"),
            ("TXN-84918", "C-F302", "M-M318", 1280, "Bengaluru", "Wallet", 22, "ALLOWED", "D-P07", "2026-08-26T16:41:50Z"),
            ("TXN-84917", "C-B73C", "M-M442", 8750, "Hyderabad", "UPI", 64, "HOLD", "D-Q41", "2026-08-26T16:41:39Z"),
        ])
    if connection.execute("SELECT COUNT(*) FROM attacks").fetchone()[0] == 0:
        connection.executemany("INSERT INTO attacks (id, name, severity, status, accounts, devices, merchants, transactions, created_at, attack_type, parameters, attack_score, detection_probability, evasion_success, generation) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", [
            ("EV-0418", "Velocity Attack", "CRITICAL", "CONTAINED", 14, 5, 8, 921, "2026-08-26T16:40:00Z", "velocity_attack", '{"transaction_velocity": 9.2}', 78, 61, 0, 1),
            ("EV-0417", "Behavioral Mimicry", "MEDIUM", "EVALUATED", 8, 3, 4, 318, "2026-08-26T16:24:00Z", "behavioral_mimicry", '{"behavioral_similarity": 0.91}', 86, 39, 1, 1),
        ])
    if connection.execute("SELECT COUNT(*) FROM incidents").fetchone()[0] == 0:
        connection.executemany("INSERT INTO incidents (id, title, severity, status, created_at, transaction_id, risk_score, reasons) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", [
            ("INC-204", "Coordinated mule network", "CRITICAL", "OPEN", "2026-08-26T16:38:00Z", "TXN-84921", 94, '["High transaction velocity", "Connected to high-risk network cluster"]'),
            ("INC-203", "Device reuse pattern", "HIGH", "INVESTIGATING", "2026-08-26T16:21:00Z", "TXN-84919", 89, '["Device linked to multiple accounts"]'),
        ])
    if connection.execute("SELECT COUNT(*) FROM threat_patterns").fetchone()[0] == 0:
        connection.executemany("INSERT INTO threat_patterns (name, description, severity) VALUES (?, ?, ?)", [
            ("Velocity burst", "Rapid authorizations across a synthetic device cluster", "HIGH"),
            ("Mule convergence", "Multiple customers converging on one merchant relationship", "CRITICAL"),
        ])
    if connection.execute("SELECT COUNT(*) FROM model_versions").fetchone()[0] == 0:
        connection.execute(
            "INSERT INTO model_versions (version, training_samples, precision, recall, f1, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            ("v1.0", 80000, 0.9945, 0.9978, 0.9962, "2026-08-26T16:00:00Z")
        )
