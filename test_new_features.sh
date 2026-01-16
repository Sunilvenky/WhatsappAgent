#!/bin/bash
# Quick start script for testing new features

echo "=========================================="
echo "WhatsApp Agent - Feature Implementation"
echo "Phase 1 & 2 Testing Script"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
API_URL="http://localhost:3000/api/v1"
ADMIN_TOKEN="${ADMIN_TOKEN:-}"  # Set via environment variable

# Test 1: Create Tenant
echo -e "${YELLOW}[TEST 1] Creating tenant...${NC}"
TENANT_RESPONSE=$(curl -s -X POST "$API_URL/tenants/" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Company",
    "slug": "test-company",
    "domain": "test.whatsappagent.com",
    "plan": "starter"
  }')

TENANT_ID=$(echo $TENANT_RESPONSE | grep -o '"id":[0-9]*' | head -1 | grep -o '[0-9]*')

if [ ! -z "$TENANT_ID" ]; then
  echo -e "${GREEN}✓ Tenant created with ID: $TENANT_ID${NC}"
else
  echo -e "${RED}✗ Failed to create tenant${NC}"
  echo "Response: $TENANT_RESPONSE"
  exit 1
fi

# Test 2: Create API Key
echo -e "${YELLOW}[TEST 2] Creating API key for tenant...${NC}"
API_KEY_RESPONSE=$(curl -s -X POST "$API_URL/tenants/$TENANT_ID/api-keys" \
  -H "Authorization: Bearer $ADMIN_TOKEN" \
  -H "X-Tenant-ID: $TENANT_ID" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test API Key",
    "permissions": ["read", "write"],
    "rate_limit": 1000
  }')

API_KEY=$(echo $API_KEY_RESPONSE | grep -o '"key":"[^"]*' | cut -d'"' -f4)

if [ ! -z "$API_KEY" ]; then
  echo -e "${GREEN}✓ API Key created: ${API_KEY:0:20}...${NC}"
else
  echo -e "${RED}✗ Failed to create API key${NC}"
  echo "Response: $API_KEY_RESPONSE"
  exit 1
fi

# Test 3: Send OTP
echo -e "${YELLOW}[TEST 3] Sending OTP...${NC}"
OTP_RESPONSE=$(curl -s -X POST "$API_URL/otp/send" \
  -H "X-Tenant-ID: $TENANT_ID" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "phone_number": "+1234567890",
    "purpose": "signup"
  }')

OTP_ID=$(echo $OTP_RESPONSE | grep -o '"id":[0-9]*' | head -1 | grep -o '[0-9]*')

if [ ! -z "$OTP_ID" ]; then
  echo -e "${GREEN}✓ OTP sent (ID: $OTP_ID)${NC}"
  echo "   Phone: +1234567890"
  echo "   Purpose: signup"
  # For testing, you would get the actual code from logs
  echo "   Note: In test mode, check application logs for OTP code"
else
  echo -e "${RED}✗ Failed to send OTP${NC}"
  echo "Response: $OTP_RESPONSE"
fi

# Test 4: Create Invoice
echo -e "${YELLOW}[TEST 4] Creating invoice...${NC}"
INVOICE_RESPONSE=$(curl -s -X POST "$API_URL/invoices" \
  -H "X-Tenant-ID: $TENANT_ID" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "invoice_number": "INV-TEST-001",
    "amount": 99.99,
    "currency": "USD",
    "due_date": "2026-02-14T00:00:00",
    "description": "Test Invoice",
    "items": "Service: WhatsApp Messages (1000 @ 0.05 USD)"
  }')

INVOICE_ID=$(echo $INVOICE_RESPONSE | grep -o '"id":[0-9]*' | head -1 | grep -o '[0-9]*')

if [ ! -z "$INVOICE_ID" ]; then
  echo -e "${GREEN}✓ Invoice created with ID: $INVOICE_ID${NC}"
else
  echo -e "${RED}✗ Failed to create invoice${NC}"
  echo "Response: $INVOICE_RESPONSE"
fi

# Test 5: Create Order
echo -e "${YELLOW}[TEST 5] Creating order...${NC}"
ORDER_RESPONSE=$(curl -s -X POST "$API_URL/orders" \
  -H "X-Tenant-ID: $TENANT_ID" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "order_number": "ORD-TEST-001",
    "total_amount": 49.99,
    "currency": "USD",
    "external_id": "shopify-12345",
    "external_platform": "shopify",
    "items": [
      {
        "sku": "SKU-001",
        "product_name": "Test Product",
        "quantity": 2,
        "price": 24.99
      }
    ]
  }')

ORDER_ID=$(echo $ORDER_RESPONSE | grep -o '"id":[0-9]*' | head -1 | grep -o '[0-9]*')

if [ ! -z "$ORDER_ID" ]; then
  echo -e "${GREEN}✓ Order created with ID: $ORDER_ID${NC}"
else
  echo -e "${RED}✗ Failed to create order${NC}"
  echo "Response: $ORDER_RESPONSE"
fi

# Test 6: Get Usage Stats
echo -e "${YELLOW}[TEST 6] Getting usage statistics...${NC}"
STATS_RESPONSE=$(curl -s -X GET "$API_URL/tenants/$TENANT_ID/usage/stats" \
  -H "X-Tenant-ID: $TENANT_ID" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json")

PLAN=$(echo $STATS_RESPONSE | grep -o '"plan":"[^"]*' | cut -d'"' -f4)

if [ ! -z "$PLAN" ]; then
  echo -e "${GREEN}✓ Usage stats retrieved${NC}"
  echo "   Plan: $PLAN"
  echo "   Full Response: $STATS_RESPONSE"
else
  echo -e "${RED}✗ Failed to get usage stats${NC}"
  echo "Response: $STATS_RESPONSE"
fi

echo ""
echo "=========================================="
echo -e "${GREEN}Testing Complete!${NC}"
echo "=========================================="
echo ""
echo "Summary:"
echo "  Tenant ID: $TENANT_ID"
echo "  API Key: ${API_KEY:0:20}..."
echo "  OTP ID: $OTP_ID"
echo "  Invoice ID: $INVOICE_ID"
echo "  Order ID: $ORDER_ID"
echo ""
echo "Next Steps:"
echo "  1. View API documentation: http://localhost:3000/docs"
echo "  2. Check database: psql postgresql://postgres:postgres@localhost:5432/whatsapp_agent"
echo "  3. Review logs: docker-compose logs -f api"
echo ""
