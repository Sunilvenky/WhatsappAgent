from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime
from apps.api.app.models.agent import AgentType, AgentStatus

# Shared properties
class AgentBase(BaseModel):
    name: Optional[str] = None
    agent_type: Optional[AgentType] = AgentType.GENERAL_SUPPORT
    system_prompt: Optional[str] = None
    configuration: Optional[Dict[str, Any]] = {}

# Properties to receive on creation
class AgentCreate(AgentBase):
    name: str

# Properties to receive on update
class AgentUpdate(AgentBase):
    status: Optional[AgentStatus] = None
    process_id: Optional[int] = None

# Properties to return to client
class AgentInDBBase(AgentBase):
    id: int
    tenant_id: int
    status: AgentStatus
    process_id: Optional[int] = None
    last_active: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Additional properties to return via API
class Agent(AgentInDBBase):
    pass

# Control schemas
class AgentAction(BaseModel):
    action: str = Field(..., pattern="^(start|stop|restart|pause)$")
