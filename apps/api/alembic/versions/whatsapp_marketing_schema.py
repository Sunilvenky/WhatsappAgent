"""Add WhatsApp marketing schema - contacts, campaigns, messages, etc.

Revision ID: whatsapp_marketing_schema
Revises: 6f5e26031965
Create Date: 2025-10-23 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'whatsapp_marketing_schema'
down_revision: Union[str, None] = '6f5e26031965'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create contacts table
    op.create_table('contacts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=False),
        sa.Column('last_name', sa.String(length=100), nullable=True),
        sa.Column('email', sa.String(length=255), nullable=True),
        sa.Column('company', sa.String(length=255), nullable=True),
        sa.Column('job_title', sa.String(length=255), nullable=True),
        sa.Column('opt_in_status', sa.Boolean(), nullable=False, default=True),
        sa.Column('opt_in_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('opt_out_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('tags', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('source', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('last_contacted', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_contact_name', 'contacts', ['first_name', 'last_name'])
    op.create_index('idx_contact_company', 'contacts', ['company'])
    op.create_index('idx_contact_opt_status', 'contacts', ['opt_in_status'])
    op.create_index('idx_contact_created', 'contacts', ['created_at'])
    op.create_index('idx_contact_last_contacted', 'contacts', ['last_contacted'])
    op.create_index(op.f('ix_contacts_email'), 'contacts', ['email'], unique=True)
    op.create_index(op.f('ix_contacts_first_name'), 'contacts', ['first_name'])
    op.create_index(op.f('ix_contacts_id'), 'contacts', ['id'])
    op.create_index(op.f('ix_contacts_last_name'), 'contacts', ['last_name'])

    # Create phone_numbers table
    op.create_table('phone_numbers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('contact_id', sa.Integer(), nullable=False),
        sa.Column('number', sa.String(length=20), nullable=False),
        sa.Column('country_code', sa.String(length=5), nullable=False),
        sa.Column('type', sa.String(length=20), nullable=False, default='mobile'),
        sa.Column('is_whatsapp_verified', sa.Boolean(), nullable=False, default=False),
        sa.Column('whatsapp_id', sa.String(length=100), nullable=True),
        sa.Column('is_primary', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('verification_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['contact_id'], ['contacts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_phone_number', 'phone_numbers', ['number'])
    op.create_index('idx_phone_contact', 'phone_numbers', ['contact_id'])
    op.create_index('idx_phone_whatsapp', 'phone_numbers', ['is_whatsapp_verified'])
    op.create_index('idx_phone_primary', 'phone_numbers', ['is_primary'])
    op.create_index('idx_phone_whatsapp_id', 'phone_numbers', ['whatsapp_id'])
    op.create_index(op.f('ix_phone_numbers_id'), 'phone_numbers', ['id'])
    op.create_index(op.f('ix_phone_numbers_whatsapp_id'), 'phone_numbers', ['whatsapp_id'], unique=True)

    # Create campaigns table
    op.create_table('campaigns',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('type', sa.String(length=20), nullable=False, default='broadcast'),
        sa.Column('status', sa.String(length=20), nullable=False, default='draft'),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('scheduled_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('ended_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('target_criteria', sa.JSON(), nullable=True),
        sa.Column('message_template', sa.Text(), nullable=False),
        sa.Column('personalization_fields', sa.JSON(), nullable=True),
        sa.Column('send_immediately', sa.Boolean(), nullable=False, default=False),
        sa.Column('respect_time_zones', sa.Boolean(), nullable=False, default=True),
        sa.Column('send_time_start', sa.String(length=5), nullable=True, default='09:00'),
        sa.Column('send_time_end', sa.String(length=5), nullable=True, default='18:00'),
        sa.Column('total_recipients', sa.Integer(), nullable=False, default=0),
        sa.Column('messages_sent', sa.Integer(), nullable=False, default=0),
        sa.Column('messages_delivered', sa.Integer(), nullable=False, default=0),
        sa.Column('messages_read', sa.Integer(), nullable=False, default=0),
        sa.Column('replies_received', sa.Integer(), nullable=False, default=0),
        sa.Column('opt_outs', sa.Integer(), nullable=False, default=0),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['created_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_campaign_name', 'campaigns', ['name'])
    op.create_index('idx_campaign_status', 'campaigns', ['status'])
    op.create_index('idx_campaign_type', 'campaigns', ['type'])
    op.create_index('idx_campaign_creator', 'campaigns', ['created_by'])
    op.create_index('idx_campaign_scheduled', 'campaigns', ['scheduled_at'])
    op.create_index('idx_campaign_created', 'campaigns', ['created_at'])
    op.create_index(op.f('ix_campaigns_id'), 'campaigns', ['id'])

    # Create conversations table
    op.create_table('conversations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('contact_id', sa.Integer(), nullable=False),
        sa.Column('assigned_to', sa.Integer(), nullable=True),
        sa.Column('subject', sa.String(length=255), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, default='active'),
        sa.Column('priority', sa.String(length=10), nullable=False, default='medium'),
        sa.Column('whatsapp_conversation_id', sa.String(length=255), nullable=True),
        sa.Column('last_message_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_message_from_contact', sa.Boolean(), nullable=False, default=False),
        sa.Column('unread_count', sa.Integer(), nullable=False, default=0),
        sa.Column('tags', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('closed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['assigned_to'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['contact_id'], ['contacts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_conversation_contact', 'conversations', ['contact_id'])
    op.create_index('idx_conversation_assigned', 'conversations', ['assigned_to'])
    op.create_index('idx_conversation_status', 'conversations', ['status'])
    op.create_index('idx_conversation_last_message', 'conversations', ['last_message_at'])
    op.create_index('idx_conversation_priority', 'conversations', ['priority'])
    op.create_index('idx_conversation_created', 'conversations', ['created_at'])
    op.create_index('idx_conversation_whatsapp_id', 'conversations', ['whatsapp_conversation_id'])
    op.create_index(op.f('ix_conversations_id'), 'conversations', ['id'])
    op.create_index(op.f('ix_conversations_whatsapp_conversation_id'), 'conversations', ['whatsapp_conversation_id'], unique=True)

    # Create leads table
    op.create_table('leads',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('contact_id', sa.Integer(), nullable=False),
        sa.Column('assigned_to', sa.Integer(), nullable=True),
        sa.Column('campaign_id', sa.Integer(), nullable=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, default='new'),
        sa.Column('priority', sa.String(length=10), nullable=False, default='medium'),
        sa.Column('source', sa.String(length=50), nullable=False, default='whatsapp_campaign'),
        sa.Column('estimated_value', sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column('currency', sa.String(length=3), nullable=False, default='USD'),
        sa.Column('probability', sa.Integer(), nullable=False, default=10),
        sa.Column('expected_close_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('actual_close_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_contact_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('next_follow_up', sa.DateTime(timezone=True), nullable=True),
        sa.Column('lead_score', sa.Integer(), nullable=False, default=0),
        sa.Column('qualification_notes', sa.Text(), nullable=True),
        sa.Column('pain_points', sa.JSON(), nullable=True),
        sa.Column('budget_range', sa.String(length=100), nullable=True),
        sa.Column('decision_maker', sa.Boolean(), nullable=False, default=False),
        sa.Column('conversion_source', sa.String(length=100), nullable=True),
        sa.Column('utm_source', sa.String(length=100), nullable=True),
        sa.Column('utm_medium', sa.String(length=100), nullable=True),
        sa.Column('utm_campaign', sa.String(length=100), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('tags', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['assigned_to'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['contact_id'], ['contacts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_lead_contact', 'leads', ['contact_id'])
    op.create_index('idx_lead_assigned', 'leads', ['assigned_to'])
    op.create_index('idx_lead_campaign', 'leads', ['campaign_id'])
    op.create_index('idx_lead_status', 'leads', ['status'])
    op.create_index('idx_lead_priority', 'leads', ['priority'])
    op.create_index('idx_lead_source', 'leads', ['source'])
    op.create_index('idx_lead_score', 'leads', ['lead_score'])
    op.create_index('idx_lead_expected_close', 'leads', ['expected_close_date'])
    op.create_index('idx_lead_created', 'leads', ['created_at'])
    op.create_index('idx_lead_title', 'leads', ['title'])
    op.create_index(op.f('ix_leads_id'), 'leads', ['id'])

    # Create messages table
    op.create_table('messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('campaign_id', sa.Integer(), nullable=True),
        sa.Column('conversation_id', sa.Integer(), nullable=False),
        sa.Column('phone_number_id', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('message_type', sa.String(length=20), nullable=False, default='text'),
        sa.Column('direction', sa.String(length=10), nullable=False, default='outbound'),
        sa.Column('whatsapp_message_id', sa.String(length=255), nullable=True),
        sa.Column('whatsapp_status', sa.String(length=20), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, default='pending'),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('delivered_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('read_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('failed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('error_code', sa.String(length=50), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('retry_count', sa.Integer(), nullable=False, default=0),
        sa.Column('max_retries', sa.Integer(), nullable=False, default=3),
        sa.Column('media_url', sa.String(length=500), nullable=True),
        sa.Column('media_type', sa.String(length=50), nullable=True),
        sa.Column('media_size', sa.Integer(), nullable=True),
        sa.Column('template_name', sa.String(length=255), nullable=True),
        sa.Column('template_variables', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['phone_number_id'], ['phone_numbers.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_message_campaign', 'messages', ['campaign_id'])
    op.create_index('idx_message_conversation', 'messages', ['conversation_id'])
    op.create_index('idx_message_phone', 'messages', ['phone_number_id'])
    op.create_index('idx_message_status', 'messages', ['status'])
    op.create_index('idx_message_direction', 'messages', ['direction'])
    op.create_index('idx_message_created', 'messages', ['created_at'])
    op.create_index('idx_message_sent', 'messages', ['sent_at'])
    op.create_index('idx_message_whatsapp_id', 'messages', ['whatsapp_message_id'])
    op.create_index(op.f('ix_messages_id'), 'messages', ['id'])
    op.create_index(op.f('ix_messages_whatsapp_message_id'), 'messages', ['whatsapp_message_id'], unique=True)

    # Create replies table
    op.create_table('replies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('conversation_id', sa.Integer(), nullable=False),
        sa.Column('original_message_id', sa.Integer(), nullable=True),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('whatsapp_message_id', sa.String(length=255), nullable=True),
        sa.Column('reply_type', sa.String(length=20), nullable=True),
        sa.Column('sentiment_score', sa.String(length=10), nullable=True),
        sa.Column('intent', sa.String(length=100), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, default='new'),
        sa.Column('is_processed', sa.Boolean(), nullable=False, default=False),
        sa.Column('processed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('processed_by', sa.Integer(), nullable=True),
        sa.Column('ai_analysis', sa.JSON(), nullable=True),
        sa.Column('confidence_score', sa.String(length=10), nullable=True),
        sa.Column('requires_response', sa.Boolean(), nullable=False, default=True),
        sa.Column('response_deadline', sa.DateTime(timezone=True), nullable=True),
        sa.Column('responded_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('response_message_id', sa.Integer(), nullable=True),
        sa.Column('received_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['original_message_id'], ['messages.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['processed_by'], ['users.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['response_message_id'], ['messages.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_reply_conversation', 'replies', ['conversation_id'])
    op.create_index('idx_reply_original_message', 'replies', ['original_message_id'])
    op.create_index('idx_reply_status', 'replies', ['status'])
    op.create_index('idx_reply_type', 'replies', ['reply_type'])
    op.create_index('idx_reply_processed', 'replies', ['is_processed'])
    op.create_index('idx_reply_received', 'replies', ['received_at'])
    op.create_index('idx_reply_requires_response', 'replies', ['requires_response'])
    op.create_index('idx_reply_whatsapp_id', 'replies', ['whatsapp_message_id'])
    op.create_index(op.f('ix_replies_id'), 'replies', ['id'])
    op.create_index(op.f('ix_replies_whatsapp_message_id'), 'replies', ['whatsapp_message_id'], unique=True)

    # Create unsubscribers table
    op.create_table('unsubscribers',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('contact_id', sa.Integer(), nullable=False),
        sa.Column('campaign_id', sa.Integer(), nullable=True),
        sa.Column('message_id', sa.Integer(), nullable=True),
        sa.Column('reason', sa.String(length=50), nullable=True),
        sa.Column('method', sa.String(length=20), nullable=False, default='reply'),
        sa.Column('feedback', sa.Text(), nullable=True),
        sa.Column('processed_by', sa.Integer(), nullable=True),
        sa.Column('trigger_message_content', sa.Text(), nullable=True),
        sa.Column('trigger_whatsapp_id', sa.String(length=255), nullable=True),
        sa.Column('confirmation_sent', sa.DateTime(timezone=True), nullable=True),
        sa.Column('resubscribe_token', sa.String(length=255), nullable=True),
        sa.Column('unsubscribed_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['contact_id'], ['contacts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['message_id'], ['messages.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['processed_by'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_unsubscriber_contact', 'unsubscribers', ['contact_id'])
    op.create_index('idx_unsubscriber_campaign', 'unsubscribers', ['campaign_id'])
    op.create_index('idx_unsubscriber_message', 'unsubscribers', ['message_id'])
    op.create_index('idx_unsubscriber_reason', 'unsubscribers', ['reason'])
    op.create_index('idx_unsubscriber_method', 'unsubscribers', ['method'])
    op.create_index('idx_unsubscriber_date', 'unsubscribers', ['unsubscribed_at'])
    op.create_index('idx_unsubscriber_token', 'unsubscribers', ['resubscribe_token'])
    op.create_index(op.f('ix_unsubscribers_id'), 'unsubscribers', ['id'])
    op.create_index(op.f('ix_unsubscribers_resubscribe_token'), 'unsubscribers', ['resubscribe_token'], unique=True)


def downgrade() -> None:
    # Drop tables in reverse order due to foreign key constraints
    op.drop_table('unsubscribers')
    op.drop_table('replies')
    op.drop_table('messages')
    op.drop_table('leads')
    op.drop_table('conversations')
    op.drop_table('campaigns')
    op.drop_table('phone_numbers')
    op.drop_table('contacts')