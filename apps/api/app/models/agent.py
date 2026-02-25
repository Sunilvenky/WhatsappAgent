"""
Agent model for autonomous subagents.
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from apps.api.app.core.database import Base


class AgentType(str, enum.Enum):
    RESEARCHER = "RESEARCHER"
    LEAD_FINDER = "LEAD_FINDER"
    CLOSER = "CLOSER"
    GENERAL_SUPPORT = "GENERAL_SUPPORT"
    CUSTOM = "CUSTOM"


class AgentStatus(str, enum.Enum):
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    STOPPED = "STOPPED"
    ERROR = "ERROR"
    PAUSED = "PAUSED"


class Agent(Base):
    """Autonomous subagent model."""
    __tablename__ = "agents"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False, index=True)
    
    name = Column(String(255), nullable=False)
    agent_type = Column(Enum(AgentType), default=AgentType.GENERAL_SUPPORT, nullable=False)
    status = Column(Enum(AgentStatus), default=AgentStatus.STOPPED, nullable=False)
    
    # Configuration and Persona
    system_prompt = Column(String, nullable=True) # The special instruction for this agent
    configuration = Column(JSON, default={}, nullable=False) # Model, temperature, etc.
    
    # Runtime info
    process_id = Column(Integer, nullable=True) # PID if running as a daemon
    last_active = Column(DateTime(timezone=True), nullable=True)
    
    # Audit
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=False)
    
    # Relationships
    tenant = relationship("Tenant", backref="agents")
    
    # Logs/Tasks would be another table, but for now we link via JSON or separate table if complex.
