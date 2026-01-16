﻿﻿# Architecture & System Design

## 🏗️ Multi-Tenant Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           WHATSAPP AGENT SAAS PLATFORM                         │
├─────────────────────────────────────────────────────────────────────────────────┤

┌─────────────────────────────────────────────────────────────────────────────────┐
│                              PRESENTATION LAYER                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │   Admin UI   │  │  Tenant UI   │  │ Mobile App  │  │  API Clients │        │
│  │   (React)    │  │   (React)    │  │  (React)    │  │ (Python, JS) │        │
│  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘        │
└─────────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              API GATEWAY LAYER                                  │
│  ┌──────────────────────────────────────────────────────────────────────────┐   │
│  │  FastAPI (Port 3000)                                                     │   │
│  │  ├─ Authentication & JWT                                                │   │
│  │  ├─ Multi-Tenancy Middleware                                            │   │
│  │  ├─ Rate Limiting                                                       │   │
│  │  ├─ Request Validation (Pydantic)                                       │   │
│  │  └─ OpenAPI/Swagger Documentation                                       │   │
│  └──────────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    ▼                 ▼                 ▼
┌────────────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│   CORE SERVICE LAYER   │  │  FEATURE MODULES │  │   INTEGRATION    │
├────────────────────────┤  ├──────────────────┤  ├──────────────────┤
│ • Auth Service         │  │ • OTP Service    │  │ • WhatsApp       │
│ • Campaign Mgmt        │  │ • Payment Mgmt   │  │   Gateway        │
│ • Contact Mgmt         │  │ • Order Mgmt     │  │ • Shopify        │
│ • Message Queue        │  │ • Drip Campaigns │  │ • WooCommerce    │
│ • ML/AI Pipelines      │  │                  │  │ • Stripe         │
└────────────────────────┘  └──────────────────┘  └──────────────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    ▼                 ▼                 ▼
┌────────────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│  DATABASE LAYER        │  │  CACHE LAYER     │  │  QUEUE LAYER     │
│ (PostgreSQL/Supabase)  │  │  (Redis)         │  │  (Celery/Redis)  │
└────────────────────────┘  └──────────────────┘  └──────────────────┘
```

---

## 🗄️ Database Schema - Simplified View

### Multi-Tenancy Core

```
                    ┌─────────────────┐
                    │   TENANTS (SaaS)│
                    └────────┬────────┘
                             │
                ┌────────────┼────────────┐
                ▼            ▼            ▼
          ┌─────────┐  ┌──────────┐  ┌──────────┐
          │TENANT   │  │API KEYS  │  │USAGE REC │
          │USERS    │  │(Auth)    │  │(Billing) │
          └─────────┘  └──────────┘  └──────────┘
                │
                │ (owns)
                ▼
    ┌───────────────────────────────┐
    │    TENANT DATA (All Tables)   │
    │                               │
    │  ┌──────────────────────────┐ │
    │  │ CONTACTS & LEADS         │ │
    │  │ ├─ Contacts              │ │
    │  │ ├─ Phone Numbers         │ │
    │  │ └─ Leads                 │ │
    │  └──────────────────────────┘ │
    │                               │
    │  ┌──────────────────────────┐ │
    │  │ CAMPAIGNS & MESSAGING    │ │
    │  │ ├─ Campaigns             │ │
    │  │ ├─ Campaign Steps (DRIP) │ │
    │  │ ├─ Messages              │ │
    │  │ ├─ Replies               │ │
    │  │ └─ Conversations         │ │
    │  └──────────────────────────┘ │
    │                               │
    │  ┌──────────────────────────┐ │
    │  │ FEATURES                 │ │
    │  │ ├─ OTP Codes             │ │
    │  │ ├─ Invoices              │ │
    │  │ ├─ Payment Reminders     │ │
    │  │ ├─ Orders                │ │
    │  │ ├─ Order Items           │ │
    │  │ └─ Packing List Messages │ │
    │  └──────────────────────────┘ │
    └───────────────────────────────┘
```

---

## 🔄 Data Flow - Example: Drip Campaign Execution

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                     DRIP CAMPAIGN EXECUTION FLOW                             │
└──────────────────────────────────────────────────────────────────────────────┘

1. API Call: Create Campaign
   ├─ POST /api/v1/campaigns
   └─ Creates: Campaign (type=drip)

2. API Call: Add Steps
   ├─ POST /api/v1/campaigns/{id}/steps
   ├─ Step 1: "Welcome" (delay: 0 hours)
   ├─ Step 2: "Tutorial" (delay: 24 hours)
   └─ Step 3: "Offer" (delay: 48 hours)

3. API Call: Enroll Contact
   ├─ POST /api/v1/contacts/{id}/campaign/{id}/enroll
   └─ Creates: ContactCampaignProgress (current_step=1)

4. Celery Task: Check Pending Steps (Runs every 5 mins)
   ├─ Query: ContactCampaignProgress WHERE status='active' 
   │          AND next_step_scheduled_at <= NOW()
   ├─ Step 1 is due now
   └─ Trigger: Send Step 1 message

5. Send Message (via WhatsApp Gateway)
   ├─ Load: Campaign Step template
   ├─ Personalize: Contact name, etc.
   ├─ Send: Via WhatsApp Gateway
   └─ Create: Message record
   └─ Update: ContactCampaignProgress
       ├─ current_step = 2
       ├─ messages_sent += 1
       ├─ next_step_scheduled_at = NOW() + 24 hours
       └─ last_step_at = NOW()

6. Celery Task: Check Pending Steps (24 hours later)
   └─ Step 2 is due
   └─ Repeat process...

7. Final Step Complete
   ├─ All steps sent
   └─ Update: ContactCampaignProgress.status = 'completed'

Timeline Visualization:
┌─────────────────────────────────────────────────────────────────────┐
│ Time:      T=0h                  T=24h                  T=48h       │
│            │                     │                      │           │
│ Step:      Welcome ──────→ Tutorial ──────→ Offer ──────→ Complete  │
│            Sent              Sent              Sent                 │
│            │                 │                 │                    │
│ Contact    Delivered         Delivered         Delivered            │
│ Status:    (Wait 24h)        (Wait 24h)        (Done)               │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 📊 Data Relationships

### Multi-Tenancy Isolation Pattern

```
Every data table has:
┌──────────────────────────────────────────┐
│ RECORD (e.g., Contact, Invoice, Order)   │
├──────────────────────────────────────────┤
│ id (PK)                                  │
│ tenant_id (FK) ───────────┐              │
│ created_at                │              │
│ updated_at                │              │
└──────────────────────────────────────────┘
                            │
                            ▼
                    ┌─────────────────┐
                    │ TENANT         │
                    │ ├─ id (PK)     │
                    │ ├─ name        │
                    │ ├─ plan        │
                    │ └─ settings    │
                    └─────────────────┘

Query Pattern (ALWAYS):
db.query(Contact)
  .filter(Contact.tenant_id == current_tenant.id)
  .all()
```

---

## 🔐 Security Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                      SECURITY LAYERS                               │
└─────────────────────────────────────────────────────────────────────┘

Layer 1: Request Authentication
┌─────────────────────────────────────────┐
│ Token (JWT) or API Key (SHA256 Hash)   │
│ ├─ Validate signature                  │
│ ├─ Check expiration                    │
│ └─ Resolve user/tenant                 │
└─────────────────────────────────────────┘
         │
         ▼
Layer 2: Tenant Authorization
┌─────────────────────────────────────────┐
│ Check user belongs to requested tenant  │
│ ├─ Query TenantUser                    │
│ ├─ Verify is_active = true             │
│ └─ Return current_tenant               │
└─────────────────────────────────────────┘
         │
         ▼
Layer 3: Data Isolation
┌─────────────────────────────────────────┐
│ Filter all queries by tenant_id         │
│ ├─ Contact.tenant_id == current_tenant  │
│ ├─ Campaign.tenant_id == current_tenant │
│ ├─ Order.tenant_id == current_tenant    │
│ └─ etc.                                 │
└─────────────────────────────────────────┘
         │
         ▼
Layer 4: Audit Logging (To implement)
┌─────────────────────────────────────────┐
│ Log all data access & modifications     │
│ ├─ User ID, Tenant ID                  │
│ ├─ Action (CREATE, UPDATE, DELETE)     │
│ ├─ Timestamp                           │
│ └─ Changes (before/after)              │
└─────────────────────────────────────────┘
```

---

## 🚀 Deployment Architecture - Oracle + Supabase

```
                    ┌─────────────────────────────┐
                    │   ORACLE FREE TIER (4 CPU) │
                    └────────────┬────────────────┘
                                 │
                ┌────────────────┼────────────────┐
                ▼                ▼                ▼
            ┌──────┐        ┌──────┐        ┌──────┐
            │ API  │        │Gateway       │Workers│
            │ Port │        │Port 3001     │       │
            │3000  │        │              │       │
            └──────┘        └──────┘        └──────┘
                │                 │                │
                └────────────────────────────────┬─┘
                                                 │
                        ┌────────────────────────┘
                        │
                        ▼
            ┌───────────────────────────┐
            │  SUPABASE (Free Tier)    │
            ├───────────────────────────┤
            │ PostgreSQL DB             │
            │ ├─ All tenant data       │
            │ ├─ Backups               │
            │ └─ Row-level security    │
            │                           │
            │ Storage (S3-like)         │
            │ ├─ Media files           │
            │ ├─ Message attachments   │
            │ └─ Order documents       │
            │                           │
            │ Auth (Optional)           │
            │ └─ JWT signing           │
            │                           │
            │ Realtime (Optional)       │
            │ └─ Webhooks              │
            └───────────────────────────┘

Configuration:
┌───────────────────────────────────────────────────┐
│ Oracle Compute:                                   │
│ - Image: Ubuntu 22.04 LTS (ARM64)                │
│ - Docker: FastAPI + WhatsApp Gateway             │
│ - Redis: In-container or separate               │
│                                                   │
│ Supabase Connection:                            │
│ - DATABASE_URL=postgresql://<user>:<pass>@<host> │
│ - CONNECTION_POOL=20 (Supabase free tier limit) │
│                                                   │
│ Environment:                                     │
│ - SUPABASE_KEY=<anon-key>                       │
│ - SUPABASE_SERVICE_ROLE=<service-key>           │
│ - WHATSAPP_GATEWAY_URL=http://localhost:3001    │
└───────────────────────────────────────────────────┘
```

---

## 🎯 Request Flow - Multi-Tenant API Call

```
┌────────────────────────────────────────────────────────────────────┐
│        CLIENT REQUEST: GET /api/v1/contacts (with API Key)        │
└────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
            ┌──────────────────────────────────┐
            │ FastAPI Request Handler          │
            │ ├─ Extract headers               │
            │ │  ├─ X-API-Key: abc123...      │
            │ │  └─ X-Tenant-ID: (optional)  │
            │ └─ Route to endpoint            │
            └──────────────────────────────────┘
                               │
                               ▼
            ┌──────────────────────────────────┐
            │ Dependency 1: get_db()            │
            │ └─ Get database connection       │
            └──────────────────────────────────┘
                               │
                               ▼
            ┌──────────────────────────────────┐
            │ Dependency 2: Authenticate       │
            │ get_tenant_from_api_key()        │
            │ ├─ Hash API key                  │
            │ ├─ Query APIKey table            │
            │ ├─ Check expiry                  │
            │ ├─ Verify tenant is active      │
            │ └─ Return Tenant object         │
            └──────────────────────────────────┘
                               │
                               ▼
            ┌──────────────────────────────────┐
            │ Endpoint Handler                 │
            │ async list_contacts(             │
            │   current_tenant: Tenant,        │
            │   db: Session                    │
            │ )                                │
            └──────────────────────────────────┘
                               │
                               ▼
            ┌──────────────────────────────────┐
            │ Query Execution (AUTO-FILTERED)  │
            │ db.query(Contact)                │
            │   .filter(Contact.tenant_id ==   │
            │     current_tenant.id)           │
            │   .all()                         │
            └──────────────────────────────────┘
                               │
                               ▼
            ┌──────────────────────────────────┐
            │ Response                         │
            │ ├─ Status: 200 OK                │
            │ ├─ Body: [Contact, Contact, ...] │
            │ └─ Headers: Content-Type: JSON   │
            └──────────────────────────────────┘
```

---

## 📈 Scaling Architecture (Future)

```
Current (Phase 2 - Complete):
┌─────────────┐
│ Single      │
│ Oracle VM   │
│ + Supabase  │
└─────────────┘

Phase 3+ (Horizontal Scaling):

┌──────────────────────────────────────────────┐
│        Oracle Cloud Always Free Tier          │
│  (4 CPUs, 24GB RAM - 2x instances possible)  │
├──────────────────────────────────────────────┤
│                                              │
│  ┌──────────────┐   ┌──────────────┐        │
│  │  API Pod 1   │   │  API Pod 2   │        │
│  │  (FastAPI)   │   │  (FastAPI)   │        │
│  └───────┬──────┘   └──────┬───────┘        │
│          │                 │                │
│          └────────────┬────┘                │
│                       │                    │
│          ┌────────────▼────────────┐        │
│          │  Load Balancer (Nginx)  │        │
│          └────────────┬────────────┘        │
│                       │                    │
└───────────────────────┼────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        ▼               ▼               ▼
    ┌─────────┐   ┌──────────┐    ┌─────────┐
    │ Redis   │   │Supabase  │    │ Storage │
    │ Cache   │   │PostgreSQL│    │  (S3)   │
    └─────────┘   └──────────┘    └─────────┘

Phase 4+ (Microservices - Not needed yet):

┌─────────────────────────────────────────────┐
│  Kubernetes (or Nomad on Oracle Free Tier)  │
├──────────────────────┬──────────────────────┤
│ API Service          │ Worker Service       │
│ (Fast API replicas)  │ (Celery replicas)    │
│                      │                      │
│ Campaign Service     │ Payment Service      │
│ (Drip automation)    │ (Invoice + reminders)│
│                      │                      │
│ WebSocket Service    │ ML Service           │
│ (Real-time updates)  │ (Model serving)      │
└─────────────────────┬──────────────────────┘
                      │
         ┌────────────┼────────────┐
         ▼            ▼            ▼
     PostgreSQL   Redis      Elasticsearch
      (Cluster)  (Cluster)     (Logs)
```

---

## 🔗 Integration Points

### Incoming Webhooks
```
Shopify Order
   │
   ▼ POST /api/v1/webhooks/shopify/orders
   │
   ├─ Create Order record
   ├─ Create OrderItems
   ├─ Add to queue: Send packing list
   └─ Schedule shipping reminder
```

### Outgoing Webhooks
```
Contact event (e.g., conversion)
   │
   ├─ Trigger payload
   ├─ Find subscribed webhook endpoints
   ├─ Queue delivery attempts
   └─ Retry on failure (exp backoff)
```

### External APIs Called
```
FastAPI → WhatsApp Gateway (local)
       → Stripe (payments)
       → AWS S3 (media storage)
       → Sentry (error tracking)
```

---

**Last Updated:** January 14, 2026  
**Status:** Phase 1 & 2 Architecture Complete
