import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, Text, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import JSON


class Base(DeclarativeBase):
    pass


class PipelineRun(Base):
    __tablename__ = "pipeline_run"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    table_name: Mapped[str] = mapped_column(String)
    injected_failure: Mapped[str] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, default="running")  # running | awaiting_approval | resolved | failed_no_incident
    adk_session_id: Mapped[str] = mapped_column(String, nullable=True)
    adk_invocation_id: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Incident(Base):
    __tablename__ = "incident"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    pipeline_run_id: Mapped[str] = mapped_column(String, ForeignKey("pipeline_run.id"))
    root_cause: Mapped[str] = mapped_column(String)
    affected_table: Mapped[str] = mapped_column(String)
    severity: Mapped[str] = mapped_column(String)
    explanation: Mapped[str] = mapped_column(Text)
    migration_sql: Mapped[str] = mapped_column(Text, nullable=True)
    rollback_sql: Mapped[str] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String, default="pending_review")
    rows_before: Mapped[int] = mapped_column(nullable=True)
    rows_after: Mapped[int] = mapped_column(nullable=True)
    changed_sample: Mapped[list] = mapped_column(JSON, nullable=True)
    dry_run_notes: Mapped[str] = mapped_column(Text, nullable=True)


class AuditLog(Base):
    __tablename__ = "audit_log"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    incident_id: Mapped[str] = mapped_column(String, ForeignKey("incident.id"))
    action: Mapped[str] = mapped_column(String)
    actor: Mapped[str] = mapped_column(String)  # "system" or "human_reviewer"
    notes: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)





class AgentTrace(Base):
    __tablename__ = "agent_trace"
    id: Mapped[str] = mapped_column(String, primary_key=True)  # f"{run_id}:{agent_name}"
    pipeline_run_id: Mapped[str] = mapped_column(String, ForeignKey("pipeline_run.id"))
    agent_name: Mapped[str] = mapped_column(String)
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    duration_ms: Mapped[int] = mapped_column(nullable=True)
    prompt_tokens: Mapped[int] = mapped_column(nullable=True)
    completion_tokens: Mapped[int] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(String, default="started")