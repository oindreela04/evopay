from __future__ import annotations

from sqlalchemy import Float, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

TABLES = ("transactions", "customers", "merchants", "devices", "attacks", "attack_generations", "incidents", "threat_patterns", "simulation_runs", "audit_events", "model_versions")


class Base(DeclarativeBase):
	pass


class Customer(Base):
	__tablename__ = "customers"
	id: Mapped[str] = mapped_column(String, primary_key=True)
	name: Mapped[str] = mapped_column(String)
	city: Mapped[str] = mapped_column(String)


class Merchant(Base):
	__tablename__ = "merchants"
	id: Mapped[str] = mapped_column(String, primary_key=True)
	name: Mapped[str] = mapped_column(String)
	city: Mapped[str] = mapped_column(String)


class Device(Base):
	__tablename__ = "devices"
	id: Mapped[str] = mapped_column(String, primary_key=True)
	platform: Mapped[str] = mapped_column(String)
	risk_score: Mapped[int] = mapped_column(Integer)


class Transaction(Base):
	__tablename__ = "transactions"
	id: Mapped[str] = mapped_column(String, primary_key=True)
	customer_id: Mapped[str] = mapped_column(String)
	merchant_id: Mapped[str] = mapped_column(String)
	amount: Mapped[int] = mapped_column(Integer)
	location: Mapped[str] = mapped_column(String)
	payment_method: Mapped[str] = mapped_column(String)
	risk_score: Mapped[int] = mapped_column(Integer)
	status: Mapped[str] = mapped_column(String)
	device_id: Mapped[str] = mapped_column(String)
	created_at: Mapped[str] = mapped_column(String)


class Attack(Base):
	__tablename__ = "attacks"
	id: Mapped[str] = mapped_column(String, primary_key=True)
	name: Mapped[str] = mapped_column(String)
	severity: Mapped[str] = mapped_column(String)
	status: Mapped[str] = mapped_column(String)
	accounts: Mapped[int] = mapped_column(Integer)
	devices: Mapped[int] = mapped_column(Integer)
	merchants: Mapped[int] = mapped_column(Integer)
	transactions: Mapped[int] = mapped_column(Integer)
	created_at: Mapped[str] = mapped_column(String)
	attack_type: Mapped[str | None] = mapped_column(String, default="composite_attack")
	parameters: Mapped[str | None] = mapped_column(Text, default="{}")
	attack_score: Mapped[int | None] = mapped_column(Integer, default=0)
	detection_probability: Mapped[int | None] = mapped_column(Integer, default=0)
	evasion_success: Mapped[int | None] = mapped_column(Integer, default=0)
	generation: Mapped[int | None] = mapped_column(Integer, default=1)


class Incident(Base):
	__tablename__ = "incidents"
	id: Mapped[str] = mapped_column(String, primary_key=True)
	title: Mapped[str] = mapped_column(String)
	severity: Mapped[str] = mapped_column(String)
	status: Mapped[str] = mapped_column(String)
	created_at: Mapped[str] = mapped_column(String)
	transaction_id: Mapped[str | None] = mapped_column(String, nullable=True)
	attack_id: Mapped[str | None] = mapped_column(String, nullable=True)
	risk_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
	reasons: Mapped[str | None] = mapped_column(Text, default="[]")


class ThreatPattern(Base):
	__tablename__ = "threat_patterns"
	id: Mapped[int] = mapped_column(Integer, primary_key=True)
	name: Mapped[str] = mapped_column(String)
	description: Mapped[str] = mapped_column(Text)
	severity: Mapped[str] = mapped_column(String)


class SimulationRun(Base):
	__tablename__ = "simulation_runs"
	id: Mapped[str] = mapped_column(String, primary_key=True)
	status: Mapped[str] = mapped_column(String)
	stage: Mapped[int] = mapped_column(Integer)
	detection_score: Mapped[float] = mapped_column(Float)
	created_at: Mapped[str] = mapped_column(String)


class AuditEvent(Base):
	__tablename__ = "audit_events"
	id: Mapped[int] = mapped_column(Integer, primary_key=True)
	event_type: Mapped[str] = mapped_column(String)
	entity_id: Mapped[str] = mapped_column(String)
	details: Mapped[str] = mapped_column(Text)
	created_at: Mapped[str] = mapped_column(String)


class AttackGeneration(Base):
	__tablename__ = "attack_generations"
	id: Mapped[int] = mapped_column(Integer, primary_key=True)
	attack_id: Mapped[str] = mapped_column(String)
	generation: Mapped[int] = mapped_column(Integer)
	parameters: Mapped[str] = mapped_column(Text)
	attack_realism: Mapped[float] = mapped_column(Float)
	financial_impact: Mapped[float] = mapped_column(Float)
	detection_probability: Mapped[float] = mapped_column(Float)
	evasion_score: Mapped[float] = mapped_column(Float)
	created_at: Mapped[str] = mapped_column(String)


class ModelVersion(Base):
	__tablename__ = "model_versions"
	id: Mapped[int] = mapped_column(Integer, primary_key=True)
	version: Mapped[str] = mapped_column(String)
	training_samples: Mapped[int] = mapped_column(Integer)
	precision: Mapped[float] = mapped_column(Float)
	recall: Mapped[float] = mapped_column(Float)
	f1: Mapped[float] = mapped_column(Float)
	created_at: Mapped[str] = mapped_column(String)
