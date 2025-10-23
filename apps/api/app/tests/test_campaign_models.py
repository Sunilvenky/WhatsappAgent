"""Tests for Campaign model and CRUD operations."""

import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from apps.api.app.models.campaign import Campaign, CampaignStatus, CampaignType
from apps.api.app.models.user import User, UserRole
from apps.api.app.crud.campaign import campaign_crud
from apps.api.app.auth.utils import get_password_hash


class TestCampaignModel:
    """Test Campaign model functionality."""

    def test_create_campaign(self, db: Session):
        """Test creating a campaign."""
        # Create a user first
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password=get_password_hash("password"),
            role=UserRole.MARKETER
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        campaign_data = {
            "name": "Test Campaign",
            "description": "A test campaign",
            "type": CampaignType.BROADCAST,
            "message_template": "Hello {{first_name}}!",
            "created_by": user.id,
        }
        
        campaign = Campaign(**campaign_data)
        db.add(campaign)
        db.commit()
        db.refresh(campaign)
        
        assert campaign.id is not None
        assert campaign.name == "Test Campaign"
        assert campaign.type == CampaignType.BROADCAST
        assert campaign.status == CampaignStatus.DRAFT
        assert campaign.is_active is False

    def test_campaign_start(self, db: Session):
        """Test starting a campaign."""
        user = User(
            email="marketer@example.com",
            username="marketer",
            hashed_password=get_password_hash("password"),
            role=UserRole.MARKETER
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        campaign = Campaign(
            name="Start Test",
            message_template="Test message",
            created_by=user.id,
            status=CampaignStatus.DRAFT
        )
        db.add(campaign)
        db.commit()
        
        # Start campaign
        campaign.start()
        db.commit()
        
        assert campaign.status == CampaignStatus.RUNNING
        assert campaign.started_at is not None
        assert campaign.is_active is True

    def test_campaign_analytics_properties(self, db: Session):
        """Test campaign analytics properties."""
        user = User(
            email="analytics@example.com",
            username="analytics",
            hashed_password=get_password_hash("password"),
            role=UserRole.MARKETER
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        campaign = Campaign(
            name="Analytics Test",
            message_template="Analytics message",
            created_by=user.id,
            messages_sent=100,
            messages_delivered=90,
            messages_read=75,
            replies_received=15
        )
        db.add(campaign)
        db.commit()
        
        assert campaign.delivery_rate == 90.0
        assert campaign.open_rate == pytest.approx(83.33, rel=1e-2)
        assert campaign.reply_rate == pytest.approx(16.67, rel=1e-2)

    def test_campaign_complete(self, db: Session):
        """Test completing a campaign."""
        user = User(
            email="complete@example.com",
            username="complete",
            hashed_password=get_password_hash("password"),
            role=UserRole.MARKETER
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        campaign = Campaign(
            name="Complete Test",
            message_template="Complete message",
            created_by=user.id,
            status=CampaignStatus.RUNNING
        )
        db.add(campaign)
        db.commit()
        
        # Complete campaign
        campaign.complete()
        db.commit()
        
        assert campaign.status == CampaignStatus.COMPLETED
        assert campaign.ended_at is not None
        assert campaign.is_active is False


class TestCampaignCRUD:
    """Test Campaign CRUD operations."""

    def test_create_campaign_crud(self, db: Session):
        """Test creating a campaign via CRUD."""
        user = User(
            email="crud@example.com",
            username="crud",
            hashed_password=get_password_hash("password"),
            role=UserRole.MARKETER
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        campaign_data = {
            "name": "CRUD Test Campaign",
            "description": "Testing CRUD operations",
            "type": CampaignType.DRIP,
            "message_template": "Hello from CRUD!",
            "created_by": user.id,
        }
        
        campaign = campaign_crud.create(db, **campaign_data)
        
        assert campaign.id is not None
        assert campaign.name == "CRUD Test Campaign"
        assert campaign.type == CampaignType.DRIP
        assert campaign.created_by == user.id

    def test_get_campaign_by_id(self, db: Session):
        """Test getting a campaign by ID."""
        user = User(
            email="getid@example.com",
            username="getid",
            hashed_password=get_password_hash("password"),
            role=UserRole.MARKETER
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        campaign = Campaign(
            name="Get By ID Test",
            message_template="Get by ID",
            created_by=user.id
        )
        db.add(campaign)
        db.commit()
        db.refresh(campaign)
        
        retrieved = campaign_crud.get(db, campaign.id)
        
        assert retrieved is not None
        assert retrieved.id == campaign.id
        assert retrieved.name == "Get By ID Test"

    def test_get_campaigns_by_creator(self, db: Session):
        """Test getting campaigns by creator."""
        user1 = User(
            email="creator1@example.com",
            username="creator1",
            hashed_password=get_password_hash("password"),
            role=UserRole.MARKETER
        )
        user2 = User(
            email="creator2@example.com",
            username="creator2",
            hashed_password=get_password_hash("password"),
            role=UserRole.MARKETER
        )
        db.add(user1)
        db.add(user2)
        db.commit()
        db.refresh(user1)
        db.refresh(user2)
        
        campaigns = [
            Campaign(name="Campaign 1", message_template="Msg 1", created_by=user1.id),
            Campaign(name="Campaign 2", message_template="Msg 2", created_by=user1.id),
            Campaign(name="Campaign 3", message_template="Msg 3", created_by=user2.id),
        ]
        
        for campaign in campaigns:
            db.add(campaign)
        db.commit()
        
        user1_campaigns = campaign_crud.get_campaigns_by_creator(db, user1.id)
        
        assert len(user1_campaigns) == 2
        for campaign in user1_campaigns:
            assert campaign.created_by == user1.id

    def test_start_campaign_crud(self, db: Session):
        """Test starting a campaign via CRUD."""
        user = User(
            email="start@example.com",
            username="start",
            hashed_password=get_password_hash("password"),
            role=UserRole.MARKETER
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        campaign = Campaign(
            name="Start CRUD Test",
            message_template="Start message",
            created_by=user.id,
            status=CampaignStatus.DRAFT
        )
        db.add(campaign)
        db.commit()
        db.refresh(campaign)
        
        # Start campaign
        result = campaign_crud.start_campaign(db, campaign.id)
        
        assert result is True
        
        db.refresh(campaign)
        assert campaign.status == CampaignStatus.RUNNING
        assert campaign.started_at is not None

    def test_pause_campaign_crud(self, db: Session):
        """Test pausing a campaign via CRUD."""
        user = User(
            email="pause@example.com",
            username="pause",
            hashed_password=get_password_hash("password"),
            role=UserRole.MARKETER
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        campaign = Campaign(
            name="Pause CRUD Test",
            message_template="Pause message",
            created_by=user.id,
            status=CampaignStatus.RUNNING
        )
        db.add(campaign)
        db.commit()
        db.refresh(campaign)
        
        # Pause campaign
        result = campaign_crud.pause_campaign(db, campaign.id)
        
        assert result is True
        
        db.refresh(campaign)
        assert campaign.status == CampaignStatus.PAUSED

    def test_get_active_campaigns(self, db: Session):
        """Test getting active campaigns."""
        user = User(
            email="active@example.com",
            username="active",
            hashed_password=get_password_hash("password"),
            role=UserRole.MARKETER
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        campaigns = [
            Campaign(name="Active 1", message_template="Msg", created_by=user.id, status=CampaignStatus.RUNNING),
            Campaign(name="Active 2", message_template="Msg", created_by=user.id, status=CampaignStatus.SCHEDULED),
            Campaign(name="Inactive", message_template="Msg", created_by=user.id, status=CampaignStatus.DRAFT),
            Campaign(name="Completed", message_template="Msg", created_by=user.id, status=CampaignStatus.COMPLETED),
        ]
        
        for campaign in campaigns:
            db.add(campaign)
        db.commit()
        
        active_campaigns = campaign_crud.get_active_campaigns(db)
        
        assert len(active_campaigns) == 2
        for campaign in active_campaigns:
            assert campaign.status in [CampaignStatus.RUNNING, CampaignStatus.SCHEDULED]

    def test_update_campaign_stats(self, db: Session):
        """Test updating campaign statistics."""
        user = User(
            email="stats@example.com",
            username="stats",
            hashed_password=get_password_hash("password"),
            role=UserRole.MARKETER
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        campaign = Campaign(
            name="Stats Test",
            message_template="Stats message",
            created_by=user.id
        )
        db.add(campaign)
        db.commit()
        db.refresh(campaign)
        
        # Update stats
        result = campaign_crud.update_stats(
            db,
            campaign.id,
            messages_sent=50,
            messages_delivered=45,
            messages_read=35,
            replies_received=10
        )
        
        assert result is True
        
        db.refresh(campaign)
        assert campaign.messages_sent == 50
        assert campaign.messages_delivered == 45
        assert campaign.messages_read == 35
        assert campaign.replies_received == 10

    def test_increment_campaign_stats(self, db: Session):
        """Test incrementing campaign statistics."""
        user = User(
            email="increment@example.com",
            username="increment",
            hashed_password=get_password_hash("password"),
            role=UserRole.MARKETER
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        campaign = Campaign(
            name="Increment Test",
            message_template="Increment message",
            created_by=user.id,
            messages_sent=10,
            messages_delivered=8
        )
        db.add(campaign)
        db.commit()
        db.refresh(campaign)
        
        # Increment stats
        result = campaign_crud.increment_stats(
            db,
            campaign.id,
            messages_sent=5,
            messages_delivered=4,
            replies_received=2
        )
        
        assert result is True
        
        db.refresh(campaign)
        assert campaign.messages_sent == 15
        assert campaign.messages_delivered == 12
        assert campaign.replies_received == 2

    def test_search_campaigns(self, db: Session):
        """Test searching campaigns."""
        user = User(
            email="search@example.com",
            username="search",
            hashed_password=get_password_hash("password"),
            role=UserRole.MARKETER
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        campaigns = [
            Campaign(name="Holiday Campaign", description="Holiday promotion", message_template="Msg", created_by=user.id),
            Campaign(name="Summer Sale", description="Summer discount", message_template="Msg", created_by=user.id),
            Campaign(name="Product Launch", description="New product announcement", message_template="Msg", created_by=user.id),
        ]
        
        for campaign in campaigns:
            db.add(campaign)
        db.commit()
        
        # Search by name
        results = campaign_crud.get_multi(db, search="Holiday")
        assert len(results) == 1
        assert results[0].name == "Holiday Campaign"
        
        # Search by description
        results = campaign_crud.get_multi(db, search="product")
        assert len(results) == 2  # "Product Launch" and "Summer Sale" (product in description)