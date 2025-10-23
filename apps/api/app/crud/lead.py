"""CRUD operations for Lead model."""

from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from apps.api.app.models.lead import Lead, LeadStatus, LeadSource, LeadPriority


class LeadCRUD:
    """CRUD operations for Lead model."""

    def create(self, db: Session, **lead_data) -> Lead:
        """Create a new lead."""
        lead = Lead(**lead_data)
        db.add(lead)
        db.commit()
        db.refresh(lead)
        return lead

    def get(self, db: Session, lead_id: int) -> Optional[Lead]:
        """Get a lead by ID."""
        return db.query(Lead).filter(Lead.id == lead_id).first()

    def get_by_contact(self, db: Session, contact_id: int) -> List[Lead]:
        """Get all leads for a contact."""
        return db.query(Lead).filter(
            Lead.contact_id == contact_id
        ).order_by(Lead.created_at.desc()).all()

    def get_multi(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        assigned_to: Optional[int] = None,
        status: Optional[LeadStatus] = None,
        priority: Optional[LeadPriority] = None,
        source: Optional[LeadSource] = None,
        search: Optional[str] = None
    ) -> List[Lead]:
        """Get multiple leads with optional filtering."""
        query = db.query(Lead)
        
        if assigned_to:
            query = query.filter(Lead.assigned_to == assigned_to)
            
        if status:
            query = query.filter(Lead.status == status)
            
        if priority:
            query = query.filter(Lead.priority == priority)
            
        if source:
            query = query.filter(Lead.source == source)
        
        if search:
            search_filter = or_(
                Lead.title.ilike(f"%{search}%"),
                Lead.description.ilike(f"%{search}%"),
                Lead.notes.ilike(f"%{search}%")
            )
            query = query.filter(search_filter)
        
        return query.order_by(Lead.created_at.desc()).offset(skip).limit(limit).all()

    def update(self, db: Session, lead: Lead, **update_data) -> Lead:
        """Update a lead."""
        for field, value in update_data.items():
            if hasattr(lead, field):
                setattr(lead, field, value)
        
        db.commit()
        db.refresh(lead)
        return lead

    def delete(self, db: Session, lead_id: int) -> bool:
        """Delete a lead."""
        lead = self.get(db, lead_id)
        if lead:
            db.delete(lead)
            db.commit()
            return True
        return False

    def get_assigned_leads(
        self, 
        db: Session, 
        user_id: int,
        status: Optional[LeadStatus] = None,
        priority: Optional[LeadPriority] = None
    ) -> List[Lead]:
        """Get leads assigned to a user."""
        query = db.query(Lead).filter(Lead.assigned_to == user_id)
        
        if status:
            query = query.filter(Lead.status == status)
            
        if priority:
            query = query.filter(Lead.priority == priority)
        
        return query.order_by(Lead.created_at.desc()).all()

    def get_open_leads(self, db: Session, user_id: Optional[int] = None) -> List[Lead]:
        """Get all open (not closed) leads."""
        query = db.query(Lead).filter(
            Lead.status.notin_([LeadStatus.CLOSED_WON, LeadStatus.CLOSED_LOST])
        )
        
        if user_id:
            query = query.filter(Lead.assigned_to == user_id)
        
        return query.order_by(Lead.created_at.desc()).all()

    def get_hot_leads(self, db: Session, user_id: Optional[int] = None) -> List[Lead]:
        """Get hot leads (high priority or high score)."""
        query = db.query(Lead).filter(
            and_(
                Lead.status.notin_([LeadStatus.CLOSED_WON, LeadStatus.CLOSED_LOST]),
                or_(
                    Lead.priority.in_([LeadPriority.HIGH, LeadPriority.URGENT]),
                    Lead.lead_score >= 80
                )
            )
        )
        
        if user_id:
            query = query.filter(Lead.assigned_to == user_id)
        
        return query.order_by(Lead.lead_score.desc()).all()

    def get_overdue_leads(self, db: Session, user_id: Optional[int] = None) -> List[Lead]:
        """Get leads with overdue follow-ups."""
        now = datetime.utcnow()
        query = db.query(Lead).filter(
            and_(
                Lead.next_follow_up < now,
                Lead.status.notin_([LeadStatus.CLOSED_WON, LeadStatus.CLOSED_LOST])
            )
        )
        
        if user_id:
            query = query.filter(Lead.assigned_to == user_id)
        
        return query.order_by(Lead.next_follow_up.asc()).all()

    def get_leads_closing_soon(
        self, 
        db: Session, 
        days: int = 30,
        user_id: Optional[int] = None
    ) -> List[Lead]:
        """Get leads expected to close within specified days."""
        future_date = datetime.utcnow() + datetime.timedelta(days=days)
        query = db.query(Lead).filter(
            and_(
                Lead.expected_close_date <= future_date,
                Lead.status.notin_([LeadStatus.CLOSED_WON, LeadStatus.CLOSED_LOST])
            )
        )
        
        if user_id:
            query = query.filter(Lead.assigned_to == user_id)
        
        return query.order_by(Lead.expected_close_date.asc()).all()

    def assign_lead(self, db: Session, lead_id: int, user_id: int) -> bool:
        """Assign a lead to a user."""
        lead = self.get(db, lead_id)
        if lead:
            lead.assign_to(user_id)
            db.commit()
            return True
        return False

    def close_won(self, db: Session, lead_id: int, actual_value: Optional[float] = None) -> bool:
        """Mark a lead as closed won."""
        lead = self.get(db, lead_id)
        if lead and lead.is_open:
            lead.close_won(actual_value)
            db.commit()
            return True
        return False

    def close_lost(self, db: Session, lead_id: int, reason: Optional[str] = None) -> bool:
        """Mark a lead as closed lost."""
        lead = self.get(db, lead_id)
        if lead and lead.is_open:
            lead.close_lost(reason)
            db.commit()
            return True
        return False

    def update_score(self, db: Session, lead_id: int, score: int) -> bool:
        """Update the lead score."""
        lead = self.get(db, lead_id)
        if lead:
            lead.update_score(score)
            db.commit()
            return True
        return False

    def schedule_follow_up(self, db: Session, lead_id: int, follow_up_date: datetime) -> bool:
        """Schedule a follow-up for the lead."""
        lead = self.get(db, lead_id)
        if lead:
            lead.schedule_follow_up(follow_up_date)
            db.commit()
            return True
        return False

    def mark_contacted(self, db: Session, lead_id: int) -> bool:
        """Mark a lead as contacted."""
        lead = self.get(db, lead_id)
        if lead:
            lead.mark_contacted()
            db.commit()
            return True
        return False

    def get_lead_stats(
        self, 
        db: Session,
        user_id: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> dict:
        """Get lead statistics."""
        query = db.query(Lead)
        
        if user_id:
            query = query.filter(Lead.assigned_to == user_id)
            
        if start_date:
            query = query.filter(Lead.created_at >= start_date)
            
        if end_date:
            query = query.filter(Lead.created_at <= end_date)
        
        leads = query.all()
        
        stats = {
            "total": len(leads),
            "open": sum(1 for l in leads if l.is_open),
            "won": sum(1 for l in leads if l.is_won),
            "lost": sum(1 for l in leads if l.is_lost),
            "hot": sum(1 for l in leads if l.is_hot),
            "overdue": sum(1 for l in leads if l.is_overdue),
            "total_value": sum(float(l.estimated_value or 0) for l in leads),
            "expected_revenue": sum(l.expected_revenue for l in leads),
            "won_value": sum(float(l.estimated_value or 0) for l in leads if l.is_won),
            "conversion_rate": (sum(1 for l in leads if l.is_won) / len(leads) * 100) if leads else 0,
        }
        
        return stats

    def search_leads(
        self, 
        db: Session, 
        query: str,
        user_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[Lead]:
        """Search leads by title, description, or notes."""
        search_filter = or_(
            Lead.title.ilike(f"%{query}%"),
            Lead.description.ilike(f"%{query}%"),
            Lead.notes.ilike(f"%{query}%")
        )
        
        db_query = db.query(Lead).filter(search_filter)
        
        if user_id:
            db_query = db_query.filter(Lead.assigned_to == user_id)
        
        return db_query.order_by(Lead.created_at.desc()).offset(skip).limit(limit).all()

    def count(
        self, 
        db: Session,
        assigned_to: Optional[int] = None,
        status: Optional[LeadStatus] = None,
        priority: Optional[LeadPriority] = None
    ) -> int:
        """Count leads with optional filtering."""
        query = db.query(Lead)
        
        if assigned_to:
            query = query.filter(Lead.assigned_to == assigned_to)
            
        if status:
            query = query.filter(Lead.status == status)
            
        if priority:
            query = query.filter(Lead.priority == priority)
        
        return query.count()


# Global instance
lead_crud = LeadCRUD()