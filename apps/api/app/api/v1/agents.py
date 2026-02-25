from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from apps.api.app.core.database import get_db
from apps.api.app.crud.agent import agent_crud
from apps.api.app.schemas.agent import Agent, AgentCreate, AgentUpdate, AgentAction
from apps.api.app.auth.dependencies import get_current_user
from apps.api.app.models.user import User
from apps.api.app.models.agent import AgentStatus

router = APIRouter()

@router.post("/", response_model=Agent, status_code=status.HTTP_201_CREATED)
def create_agent(
    agent_in: AgentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new autonomous subagent."""
    # Note: In a real multi-tenant app, we would use current_user.tenant_id
    # For now, we'll assume a default tenant (id=1) if tenant_id is not on User model yet
    tenant_id = getattr(current_user, "tenant_id", 1)
    
    db_agent = agent_crud.create(db, obj_in=agent_in.model_dump(), tenant_id=tenant_id)
    return db_agent

@router.get("/", response_model=List[Agent])
def list_agents(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all agents for the current tenant."""
    tenant_id = getattr(current_user, "tenant_id", 1)
    return agent_crud.get_multi_by_tenant(db, tenant_id=tenant_id, skip=skip, limit=limit)

@router.get("/{agent_id}", response_model=Agent)
def get_agent(
    agent_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get details of a specific agent."""
    db_agent = agent_crud.get(db, agent_id)
    if not db_agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return db_agent

@router.patch("/{agent_id}", response_model=Agent)
def update_agent(
    agent_id: int,
    agent_in: AgentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update an agent's configuration or status."""
    db_agent = agent_crud.get(db, agent_id)
    if not db_agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    return agent_crud.update(db, db_obj=db_agent, obj_in=agent_in.model_dump(exclude_unset=True))

@router.post("/{agent_id}/control", response_model=Agent)
def control_agent(
    agent_id: int,
    action_in: AgentAction,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Control the agent runtime.
    Actions: start, stop, restart, pause
    """
    db_agent = agent_crud.get(db, agent_id)
    if not db_agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    action = action_in.action
    
    if action == "start":
        # TODO: Trigger ZeroClaw process spawning
        # For now, just update status in DB
        return agent_crud.update_status(db, agent_id=agent_id, status=AgentStatus.RUNNING, pid=1234) # Dummy PID
    
    elif action == "stop":
        # TODO: Kill ZeroClaw process
        return agent_crud.update_status(db, agent_id=agent_id, status=AgentStatus.STOPPED, pid=None)
    
    elif action == "restart":
        # TODO: Stop then Start
        return agent_crud.update_status(db, agent_id=agent_id, status=AgentStatus.RUNNING)
    
    elif action == "pause":
        return agent_crud.update_status(db, agent_id=agent_id, status=AgentStatus.PAUSED)
    
    return db_agent

@router.delete("/{agent_id}", response_model=Agent)
def delete_agent(
    agent_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an agent."""
    db_agent = agent_crud.get(db, agent_id)
    if not db_agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent_crud.remove(db, id=agent_id)
