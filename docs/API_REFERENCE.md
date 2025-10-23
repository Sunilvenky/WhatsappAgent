# WhatsApp Agent API Documentation

## Overview

The WhatsApp Agent API is a comprehensive RESTful API for managing WhatsApp marketing campaigns, contacts, conversations, and leads. Built with FastAPI, it provides a complete backend solution for WhatsApp-based marketing automation.

## Features

- **Contact Management**: Create, update, and manage marketing contacts with phone number verification
- **Campaign Management**: Design, execute, and monitor WhatsApp marketing campaigns
- **Conversation Management**: Handle customer conversations and message flows
- **Lead Management**: Track and nurture leads through the sales pipeline
- **User Authentication**: JWT-based authentication with role-based access control
- **Analytics & Reporting**: Comprehensive statistics and performance metrics

## Quick Start

### Prerequisites

- Python 3.9+
- PostgreSQL database
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd whatsapp-agent
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your database and configuration settings
   ```

5. **Run database migrations**
   ```bash
   cd apps/api
   alembic upgrade head
   ```

6. **Seed sample data (optional)**
   ```bash
   python -m apps.api.app.scripts.seed_data
   ```

7. **Start the server**
   ```bash
   python -m apps.api.app.main
   ```

The API will be available at `http://localhost:8000` with interactive documentation at `http://localhost:8000/docs`.

## API Endpoints

All endpoints require authentication except for health checks and authentication endpoints.

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/login` | User login |
| POST | `/api/v1/auth/refresh` | Refresh access token |
| POST | `/api/v1/auth/register` | Register new user |

### Health & System

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/health` | Health check |
| GET | `/metrics` | Prometheus metrics |

### User Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/users/me` | Get current user profile |
| PUT | `/api/v1/users/me` | Update current user profile |
| GET | `/api/v1/users/` | List users (admin only) |
| POST | `/api/v1/users/` | Create user (admin only) |
| GET | `/api/v1/users/{user_id}` | Get user by ID |
| PUT | `/api/v1/users/{user_id}` | Update user |
| DELETE | `/api/v1/users/{user_id}` | Delete user |

### Contact Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/contacts/` | Create new contact |
| GET | `/api/v1/contacts/` | List contacts with filtering |
| GET | `/api/v1/contacts/{contact_id}` | Get contact details |
| PUT | `/api/v1/contacts/{contact_id}` | Update contact |
| DELETE | `/api/v1/contacts/{contact_id}` | Delete contact |
| POST | `/api/v1/contacts/{contact_id}/opt-in` | Opt-in contact |
| POST | `/api/v1/contacts/{contact_id}/opt-out` | Opt-out contact |
| GET | `/api/v1/contacts/{contact_id}/phone-numbers` | Get contact phone numbers |
| POST | `/api/v1/contacts/{contact_id}/phone-numbers` | Add phone number |
| PUT | `/api/v1/contacts/phone-numbers/{phone_id}` | Update phone number |
| DELETE | `/api/v1/contacts/phone-numbers/{phone_id}` | Delete phone number |
| POST | `/api/v1/contacts/phone-numbers/{phone_id}/verify` | Verify WhatsApp number |
| POST | `/api/v1/contacts/phone-numbers/{phone_id}/set-primary` | Set primary phone |
| GET | `/api/v1/contacts/bulk/opt-in-stats` | Get opt-in statistics |
| POST | `/api/v1/contacts/bulk/import` | Bulk import contacts |

### Campaign Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/campaigns/` | Create new campaign |
| GET | `/api/v1/campaigns/` | List campaigns with filtering |
| GET | `/api/v1/campaigns/{campaign_id}` | Get campaign details |
| PUT | `/api/v1/campaigns/{campaign_id}` | Update campaign |
| DELETE | `/api/v1/campaigns/{campaign_id}` | Delete campaign |
| POST | `/api/v1/campaigns/{campaign_id}/start` | Start campaign |
| POST | `/api/v1/campaigns/{campaign_id}/pause` | Pause campaign |
| POST | `/api/v1/campaigns/{campaign_id}/resume` | Resume campaign |
| POST | `/api/v1/campaigns/{campaign_id}/stop` | Stop campaign |
| POST | `/api/v1/campaigns/{campaign_id}/complete` | Mark campaign complete |
| GET | `/api/v1/campaigns/{campaign_id}/stats` | Get campaign statistics |
| PUT | `/api/v1/campaigns/{campaign_id}/stats` | Update campaign stats |
| GET | `/api/v1/campaigns/stats/overview` | Campaign overview stats |
| POST | `/api/v1/campaigns/{campaign_id}/duplicate` | Duplicate campaign |

### Conversation Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/conversations/` | Create new conversation |
| GET | `/api/v1/conversations/` | List conversations with filtering |
| GET | `/api/v1/conversations/assigned` | Get assigned conversations |
| GET | `/api/v1/conversations/urgent` | Get urgent conversations |
| GET | `/api/v1/conversations/unread` | Get unread conversations |
| GET | `/api/v1/conversations/{conversation_id}` | Get conversation details |
| PUT | `/api/v1/conversations/{conversation_id}` | Update conversation |
| DELETE | `/api/v1/conversations/{conversation_id}` | Delete conversation |
| POST | `/api/v1/conversations/{conversation_id}/assign` | Assign conversation |
| POST | `/api/v1/conversations/{conversation_id}/close` | Close conversation |
| POST | `/api/v1/conversations/{conversation_id}/reopen` | Reopen conversation |
| GET | `/api/v1/conversations/{conversation_id}/messages` | Get conversation messages |
| POST | `/api/v1/conversations/{conversation_id}/messages` | Send message |
| PUT | `/api/v1/conversations/messages/{message_id}/status` | Update message status |
| GET | `/api/v1/conversations/messages/{message_id}` | Get message details |
| POST | `/api/v1/conversations/{conversation_id}/replies` | Create reply |
| GET | `/api/v1/conversations/{conversation_id}/replies` | Get conversation replies |
| GET | `/api/v1/conversations/stats/overview` | Conversation statistics |

### Lead Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/leads/` | Create new lead |
| GET | `/api/v1/leads/` | List leads with filtering |
| GET | `/api/v1/leads/assigned` | Get assigned leads |
| GET | `/api/v1/leads/high-priority` | Get high priority leads |
| GET | `/api/v1/leads/overdue` | Get overdue leads |
| GET | `/api/v1/leads/{lead_id}` | Get lead details |
| PUT | `/api/v1/leads/{lead_id}` | Update lead |
| DELETE | `/api/v1/leads/{lead_id}` | Delete lead |
| POST | `/api/v1/leads/{lead_id}/assign` | Assign lead |
| POST | `/api/v1/leads/{lead_id}/contacted` | Mark lead as contacted |
| POST | `/api/v1/leads/{lead_id}/follow-up` | Schedule follow-up |
| POST | `/api/v1/leads/{lead_id}/score` | Update lead score |
| POST | `/api/v1/leads/{lead_id}/convert` | Convert lead (mark as won) |
| POST | `/api/v1/leads/{lead_id}/close-lost` | Close lead as lost |
| GET | `/api/v1/leads/{lead_id}/activities` | Get lead activities |
| GET | `/api/v1/leads/stats/overview` | Lead statistics overview |
| GET | `/api/v1/leads/stats/pipeline` | Sales pipeline statistics |
| GET | `/api/v1/leads/stats/conversion-funnel` | Conversion funnel stats |
| POST | `/api/v1/leads/bulk/assign` | Bulk assign leads |
| POST | `/api/v1/leads/bulk/update-status` | Bulk update lead status |

## Authentication & Authorization

The API uses JWT (JSON Web Tokens) for authentication. Include the access token in the Authorization header:

```bash
Authorization: Bearer <access_token>
```

### User Roles

- **Admin**: Full system access
- **Marketer**: Campaign and lead management
- **Sales**: Lead and conversation management
- **Viewer**: Read-only access

## Data Models

### Contact
```json
{
  "id": 1,
  "first_name": "John",
  "last_name": "Doe",
  "email": "john.doe@example.com",
  "company": "Example Corp",
  "job_title": "CEO",
  "opt_in_status": true,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Campaign
```json
{
  "id": 1,
  "name": "Product Launch",
  "description": "Q4 product launch campaign",
  "type": "broadcast",
  "status": "running",
  "message_template": "Hi {{first_name}}! Check out our new product.",
  "messages_sent": 100,
  "messages_delivered": 95,
  "messages_read": 80,
  "replies_received": 12,
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Lead
```json
{
  "id": 1,
  "title": "Enterprise Deal - Example Corp",
  "description": "Large enterprise opportunity",
  "status": "qualified",
  "priority": "high",
  "source": "whatsapp_campaign",
  "estimated_value": "50000.00",
  "probability": 75,
  "lead_score": 85,
  "assigned_to": 2,
  "contact_id": 1,
  "campaign_id": 1
}
```

## Error Handling

The API returns appropriate HTTP status codes and error messages:

```json
{
  "detail": "Error description"
}
```

Common status codes:
- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `422`: Validation Error
- `500`: Internal Server Error

## Rate Limiting

Rate limiting is implemented to prevent abuse:
- 100 requests per minute per user
- 1000 requests per hour per user

## Filtering & Pagination

Most list endpoints support filtering and pagination:

```bash
GET /api/v1/contacts/?search=john&company=example&skip=0&limit=20
```

Query parameters:
- `skip`: Number of records to skip (default: 0)
- `limit`: Maximum records to return (default: 100)
- `search`: Text search across relevant fields
- Additional filters specific to each endpoint

## Examples

### Create a Contact
```bash
curl -X POST "http://localhost:8000/api/v1/contacts/" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "John",
    "last_name": "Doe",
    "email": "john.doe@example.com",
    "company": "Example Corp",
    "opt_in_status": true
  }'
```

### Start a Campaign
```bash
curl -X POST "http://localhost:8000/api/v1/campaigns/1/start" \
  -H "Authorization: Bearer <token>"
```

### Create a Lead
```bash
curl -X POST "http://localhost:8000/api/v1/leads/" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "contact_id": 1,
    "title": "Enterprise Deal",
    "description": "Potential large enterprise customer",
    "estimated_value": "25000.00",
    "priority": "high",
    "source": "whatsapp_campaign"
  }'
```

## Development

### Running Tests
```bash
pytest apps/api/app/tests/
```

### Database Migrations
```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Code Quality
```bash
# Format code
black apps/api/

# Sort imports
isort apps/api/

# Lint code
flake8 apps/api/
```

## Deployment

### Environment Variables
```bash
DATABASE_URL=postgresql://user:password@localhost/whatsapp_agent
SECRET_KEY=your-secret-key
API_HOST=0.0.0.0
API_PORT=8000
```

### Docker
```bash
# Build image
docker build -t whatsapp-agent-api .

# Run container
docker run -d -p 8000:8000 --env-file .env whatsapp-agent-api
```

## Support

For questions or support, please check the documentation at `/docs` or contact the development team.

## License

This project is licensed under the MIT License.