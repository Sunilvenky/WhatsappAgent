"""SQLite compatible initial schema migration

Revision ID: 20260115_001
Revises: 
Create Date: 2025-01-15

This migration creates all tables for the WhatsApp marketing platform with SQLite compatibility.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import func


# revision identifiers, used by Alembic.
revision: str = '20260115_001'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create all database tables."""
    
    # ===== USERS TABLE =====
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('username', sa.String(255), nullable=False, unique=True),
        sa.Column('hashed_password', sa.String(255), nullable=False),
        sa.Column('full_name', sa.String(255), nullable=True),
        sa.Column('role', sa.String(20), nullable=False, default='marketer'),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), default=func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_users_username', 'users', ['username'], unique=True)

    # ===== TENANTS TABLE (Multi-tenancy) =====
    op.create_table(
        'tenants',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('slug', sa.String(255), nullable=False, unique=True),
        sa.Column('domain', sa.String(255), nullable=True),
        sa.Column('plan', sa.String(50), nullable=False, default='starter'),
        sa.Column('billing_customer_id', sa.String(255), nullable=True),
        sa.Column('settings', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), default=func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_tenants_slug', 'tenants', ['slug'], unique=True)

    # ===== TENANT_USERS TABLE =====
    op.create_table(
        'tenant_users',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('role', sa.String(50), nullable=False, default='member'),
        sa.Column('created_at', sa.DateTime(), default=func.now(), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_id', 'user_id', name='uq_tenant_user')
    )

    # ===== API_KEYS TABLE =====
    op.create_table(
        'api_keys',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('key', sa.String(255), nullable=False, unique=True),
        sa.Column('last_used', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(), default=func.now(), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # ===== USAGE_RECORDS TABLE =====
    op.create_table(
        'usage_records',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('api_key_id', sa.Integer(), nullable=True),
        sa.Column('endpoint', sa.String(255), nullable=False),
        sa.Column('method', sa.String(10), nullable=False),
        sa.Column('status_code', sa.Integer(), nullable=True),
        sa.Column('response_time_ms', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), default=func.now(), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['api_key_id'], ['api_keys.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    # ===== CONTACTS TABLE =====
    op.create_table(
        'contacts',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('phone_number', sa.String(20), nullable=False),
        sa.Column('name', sa.String(255), nullable=True),
        sa.Column('email', sa.String(255), nullable=True),
        sa.Column('custom_fields', sa.JSON(), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), default=func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_id', 'phone_number', name='uq_tenant_phone')
    )

    # ===== CAMPAIGNS TABLE =====
    op.create_table(
        'campaigns',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.String(2000), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, default='draft'),
        sa.Column('message_template', sa.String(5000), nullable=False),
        sa.Column('created_at', sa.DateTime(), default=func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('scheduled_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # ===== MESSAGES TABLE =====
    op.create_table(
        'messages',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('campaign_id', sa.Integer(), nullable=True),
        sa.Column('contact_id', sa.Integer(), nullable=False),
        sa.Column('direction', sa.String(10), nullable=False),
        sa.Column('content', sa.String(5000), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, default='pending'),
        sa.Column('sent_at', sa.DateTime(), nullable=True),
        sa.Column('delivered_at', sa.DateTime(), nullable=True),
        sa.Column('read_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), default=func.now(), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['contact_id'], ['contacts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # ===== CONVERSATIONS TABLE =====
    op.create_table(
        'conversations',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('contact_id', sa.Integer(), nullable=False),
        sa.Column('last_message_at', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(50), nullable=False, default='active'),
        sa.Column('created_at', sa.DateTime(), default=func.now(), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['contact_id'], ['contacts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # ===== REPLIES TABLE =====
    op.create_table(
        'replies',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('message_id', sa.Integer(), nullable=False),
        sa.Column('conversation_id', sa.Integer(), nullable=False),
        sa.Column('content', sa.String(5000), nullable=False),
        sa.Column('sentiment', sa.String(50), nullable=True),
        sa.Column('created_at', sa.DateTime(), default=func.now(), nullable=True),
        sa.ForeignKeyConstraint(['message_id'], ['messages.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['conversation_id'], ['conversations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # ===== LEADS TABLE =====
    op.create_table(
        'leads',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('contact_id', sa.Integer(), nullable=False),
        sa.Column('score', sa.Integer(), default=0),
        sa.Column('status', sa.String(50), nullable=False, default='new'),
        sa.Column('source', sa.String(100), nullable=True),
        sa.Column('created_at', sa.DateTime(), default=func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['contact_id'], ['contacts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # ===== PHONE_NUMBERS TABLE =====
    op.create_table(
        'phone_numbers',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('phone', sa.String(20), nullable=False, unique=True),
        sa.Column('is_verified', sa.Boolean(), default=False),
        sa.Column('verified_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), default=func.now(), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # ===== UNSUBSCRIBERS TABLE =====
    op.create_table(
        'unsubscribers',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('contact_id', sa.Integer(), nullable=True),
        sa.Column('phone_number', sa.String(20), nullable=False),
        sa.Column('reason', sa.String(500), nullable=True),
        sa.Column('created_at', sa.DateTime(), default=func.now(), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['contact_id'], ['contacts.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )

    # ===== OTP_CODES TABLE =====
    op.create_table(
        'otp_codes',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('phone_number', sa.String(20), nullable=False),
        sa.Column('code', sa.String(6), nullable=False),
        sa.Column('is_verified', sa.Boolean(), default=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), default=func.now(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # ===== INVOICES TABLE =====
    op.create_table(
        'invoices',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('invoice_number', sa.String(50), nullable=False, unique=True),
        sa.Column('amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, default='pending'),
        sa.Column('due_date', sa.DateTime(), nullable=True),
        sa.Column('paid_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), default=func.now(), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # ===== PAYMENT_REMINDERS TABLE =====
    op.create_table(
        'payment_reminders',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('invoice_id', sa.Integer(), nullable=False),
        sa.Column('sent_at', sa.DateTime(), default=func.now()),
        sa.Column('contact_phone', sa.String(20), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, default='pending'),
        sa.ForeignKeyConstraint(['invoice_id'], ['invoices.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # ===== ORDERS TABLE =====
    op.create_table(
        'orders',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('contact_id', sa.Integer(), nullable=False),
        sa.Column('order_number', sa.String(50), nullable=False),
        sa.Column('status', sa.String(50), nullable=False, default='pending'),
        sa.Column('total_amount', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column('created_at', sa.DateTime(), default=func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['contact_id'], ['contacts.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # ===== ORDER_ITEMS TABLE =====
    op.create_table(
        'order_items',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('product_name', sa.String(255), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('price', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # ===== PACKING_LIST_MESSAGES TABLE =====
    op.create_table(
        'packing_list_messages',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('order_id', sa.Integer(), nullable=False),
        sa.Column('message', sa.String(5000), nullable=False),
        sa.Column('sent_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), default=func.now(), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # ===== CAMPAIGN_STEPS TABLE =====
    op.create_table(
        'campaign_steps',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('campaign_id', sa.Integer(), nullable=False),
        sa.Column('step_number', sa.Integer(), nullable=False),
        sa.Column('message', sa.String(5000), nullable=False),
        sa.Column('delay_hours', sa.Integer(), default=0),
        sa.Column('created_at', sa.DateTime(), default=func.now(), nullable=True),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )

    # ===== CONTACT_CAMPAIGN_PROGRESS TABLE =====
    op.create_table(
        'contact_campaign_progress',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('contact_id', sa.Integer(), nullable=False),
        sa.Column('campaign_id', sa.Integer(), nullable=False),
        sa.Column('current_step', sa.Integer(), default=0),
        sa.Column('status', sa.String(50), nullable=False, default='started'),
        sa.Column('started_at', sa.DateTime(), default=func.now()),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['contact_id'], ['contacts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['campaign_id'], ['campaigns.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('contact_id', 'campaign_id', name='uq_contact_campaign')
    )

    # ===== DRIP_CAMPAIGNS TABLE =====
    op.create_table(
        'drip_campaigns',
        sa.Column('id', sa.Integer(), nullable=False, autoincrement=True),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.String(2000), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), default=func.now(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade() -> None:
    """Drop all created tables in reverse order."""
    op.drop_table('drip_campaigns')
    op.drop_table('contact_campaign_progress')
    op.drop_table('campaign_steps')
    op.drop_table('packing_list_messages')
    op.drop_table('order_items')
    op.drop_table('orders')
    op.drop_table('payment_reminders')
    op.drop_table('invoices')
    op.drop_table('otp_codes')
    op.drop_table('unsubscribers')
    op.drop_table('phone_numbers')
    op.drop_table('leads')
    op.drop_table('replies')
    op.drop_table('conversations')
    op.drop_table('messages')
    op.drop_table('campaigns')
    op.drop_table('contacts')
    op.drop_table('usage_records')
    op.drop_table('api_keys')
    op.drop_table('tenant_users')
    op.drop_table('tenants')
    op.drop_table('users')
