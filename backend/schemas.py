from pydantic import BaseModel
from typing import Any


class HealthResponse(BaseModel):
    status: str
    service: str


class ActionRequest(BaseModel):
    action: str


class AttackGenerateRequest(BaseModel):
    strategy: str = "Composite Attack"
    attack_type: str | None = None
    generation: int = 1


class AttackEvolveRequest(BaseModel):
    attack_id: str


class ThreatPatternRequest(BaseModel):
    name: str
    description: str
    severity: str = "MEDIUM"


class InvestigationRequest(BaseModel):
    entity_id: str | None = None
    transaction_id: str | None = None
    transaction: dict[str, Any] | None = None
    network: dict[str, Any] | None = None
    notes: str = "Manual investigation opened"


class SimulationStartRequest(BaseModel):
    attack_id: str | None = None


class DefenseAdaptRequest(BaseModel):
    pattern: str = "DEFENSE BLIND SPOT"


class IncidentActionRequest(BaseModel):
    status: str


class RiskAnalysisResponse(BaseModel):
    risk_score: int
    classification: str
    signals: dict[str, Any]
    reasons: list[str]
    recommended_action: str


class InvestigatorResponse(BaseModel):
    finding: str
    evidence: list[str]
    risk: str
    attack_type: str
    recommended_action: str
    risk_score: int
    signals: dict[str, Any]
    analysis_mode: str


class TransactionResponse(BaseModel):
    id: str
    customer_id: str
    merchant_id: str
    amount: int
    location: str
    payment_method: str
    risk_score: int
    status: str
    device_id: str
    created_at: str
    synthetic: bool = True


class IncidentResponse(BaseModel):
    id: str
    title: str
    severity: str
    status: str
    created_at: str
    transaction_id: str | None = None
    attack_id: str | None = None
    risk_score: int | None = None
    reasons: str | list[str] | None = None
    synthetic: bool = True


class AttackResponse(BaseModel):
    id: str
    name: str
    severity: str
    status: str
    accounts: int
    devices: int
    merchants: int
    transactions: int
    created_at: str
    attack_type: str | None = None
    attack_score: int | None = None
    detection_score: int | None = None
    evasion_success: int | bool | None = None
    generation: int | None = 1
    synthetic: bool = True


class SimulationResponse(BaseModel):
    id: str
    status: str
    stage: int
    detection_score: float | None
    created_at: str
    attack_id: str | None = None


class AnalyticsResponse(BaseModel):
    mean_detection_score: float | None
    false_positive_rate: float | None
    average_response_time: float | None
    daily_events: list[dict[str, Any]]
    model_version: str | None = None


class NetworkResponse(BaseModel):
    nodes: list[dict[str, Any]]
    relationships: list[dict[str, Any]]


class DefenseAdaptResponse(BaseModel):
    before_detection_score: float | None
    after_detection_score: float | None
    model_version: str | None
    pattern: str


class AuditEventResponse(BaseModel):
    id: int
    event_type: str
    entity_id: str
    details: str
    created_at: str


class ModelVersionResponse(BaseModel):
    id: int
    version: str
    training_samples: int
    precision: float
    recall: float
    f1: float
    created_at: str


class DashboardResponse(BaseModel):
    metrics: dict[str, Any]
    transactions: list[TransactionResponse]
    incidents: list[IncidentResponse]
