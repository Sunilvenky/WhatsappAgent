from typing import List, Optional, Any, Dict
from sqlalchemy.orm import Session
from sqlalchemy import and_
from apps.api.app.models.agent import Agent, AgentType, AgentStatus
from datetime import datetime

class AgentCRUD:
    """CRUD operations for Agents."""
    
    def get(self, db: Session, id: int) -> Optional[Agent]:
        return db.query(Agent).filter(Agent.id == id).first()
    
    def get_multi_by_tenant(
        self, db: Session, *, tenant_id: int, skip: int = 0, limit: int = 100
    ) -> List[Agent]:
        return (
            db.query(Agent)
            .filter(Agent.tenant_id == tenant_id)
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def create(self, db: Session, *, obj_in: Dict[str, Any], tenant_id: int) -> Agent:
        db_obj = Agent(
            tenant_id=tenant_id,
            name=obj_in.get("name"),
            agent_type=obj_in.get("agent_type", "GENERAL_SUPPORT"),
            system_prompt=obj_in.get("system_prompt"),
            configuration=obj_in.get("configuration", {}),
            status=AgentStatus.STOPPED
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update(
        self, db: Session, *, db_obj: Agent, obj_in: Dict[str, Any]
    ) -> Agent:
        for field in obj_in:
            if hasattr(db_obj, field):
                setattr(db_obj, field, obj_in[field])
        
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def remove(self, db: Session, *, id: int) -> Agent:
        obj = db.query(Agent).get(id)
        db.delete(obj)
        db.commit()
        return obj

    def update_status(self, db: Session, *, agent_id: int, status: AgentStatus, pid: Optional[int] = None) -> Optional[Agent]:
        agent = self.get(db, agent_id)
        if agent:
            agent.status = status
            if pid is not None:
                agent.process_id = pid
            agent.last_active = datetime.utcnow()
            db.add(agent)
            db.commit()
            db.refresh(agent)
        return agent

agent_crud = AgentCRUD()
