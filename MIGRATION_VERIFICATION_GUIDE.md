# ===== MIGRATION VERIFICATION & EXECUTION GUIDE =====

## Step 1: Verify PostgreSQL is Running

```powershell
# Check if Docker PostgreSQL is running
docker ps

# Should show "postgres-whatsapp" in the list

# OR if using local PostgreSQL, verify it's running
```

## Step 2: Check .env File

```powershell
# Verify .env file exists and has DATABASE_URL set
cd "e:\Sunny React Projects\Whatsapp Agent\apps\api"

# Check the file content
type .env
```

**Expected output should include:**
```
DATABASE_URL=postgresql://postgres:password@localhost:5432/whatsapp_agent
```

## Step 3: Activate Virtual Environment

```powershell
# Make sure you're in the api folder
cd "e:\Sunny React Projects\Whatsapp Agent\apps\api"

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# If it asks about execution policy, run this first:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Step 4: Check Current Migration Status

```powershell
# See which migrations have been applied
alembic current

# This might show nothing if no migrations have been applied yet
# or show "6f5e26031965" if the old migration was applied
```

## Step 5: REMOVE OLD INCOMPLETE MIGRATION (if it exists)

```powershell
# Downgrade any existing migrations first
alembic downgrade base

# This should show:
# "Downgrading from 6f5e26031965 to base"
# or nothing if there are no migrations

# Check status
alembic current
# Should show nothing now
```

## Step 6: RUN THE COMPLETE MIGRATION

```powershell
# Apply the new complete migration
alembic upgrade head

# Expected output:
# INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
# INFO  [alembic.runtime.migration] Will assume transactional DDL.
# INFO  [alembic.runtime.migration] Running upgrade  -> 20260114_001, Complete initial migration
```

## Step 7: VERIFY MIGRATION SUCCEEDED

```powershell
# Check current status
alembic current

# Should show:
# 20260114_001 (head)
```

## Step 8: VERIFY ALL TABLES WERE CREATED

**Option A: Using Docker PostgreSQL**

```powershell
# List all tables in the database
docker exec postgres-whatsapp psql -U postgres -d whatsapp_agent -c "\dt"

# Should show all 20 tables like:
# users, tenants, tenant_users, api_keys, usage_records, 
# contacts, campaigns, conversations, messages, replies, leads,
# phone_numbers, unsubscribers, otp_codes, invoices, payment_reminders,
# orders, order_items, packing_list_messages, campaign_steps, contact_campaign_progress
```

**Option B: Using Local PostgreSQL**

```powershell
# List all tables
psql -U postgres -d whatsapp_agent -c "\dt"
```

## Step 9: VERIFY TABLE STRUCTURE

```powershell
# Check structure of a specific table (e.g., users)
docker exec postgres-whatsapp psql -U postgres -d whatsapp_agent -c "\d users"

# Expected output should show columns:
# id, email, username, hashed_password, full_name, role, is_active, created_at, updated_at
```

## Step 10: COUNT ROWS IN EACH TABLE (should be 0)

```powershell
# All tables should be empty initially
docker exec postgres-whatsapp psql -U postgres -d whatsapp_agent -c "SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename;"

# Should list all 20+ table names
```

## Step 11: TEST DATABASE CONNECTION FROM PYTHON

```powershell
# Test database connection from Python
python -c "from sqlalchemy import create_engine; engine = create_engine('postgresql://postgres:password@localhost:5432/whatsapp_agent'); connection = engine.connect(); print('✅ Database connection successful!'); connection.close()"

# Should print: "✅ Database connection successful!"
```

## Step 12: START FASTAPI AND VERIFY IT CONNECTS

```powershell
# Start the FastAPI server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Expected output:
# INFO:     Uvicorn running on http://0.0.0.0:8000
# INFO:     Application startup complete
```

## Step 13: TEST API ENDPOINT

```powershell
# In another terminal, test the API
curl http://localhost:8000/health/health

# Should return:
# {"code":"ok","message":"healthy","data":{"status":"ok"}}
```

## COMPLETE VERIFICATION CHECKLIST

✅ PostgreSQL is running
✅ .env file has DATABASE_URL
✅ Virtual environment is activated
✅ alembic current shows "20260114_001"
✅ All 20 tables exist in database
✅ Tables have correct structure
✅ Database connection works from Python
✅ FastAPI starts without errors
✅ API health endpoint responds correctly

## IF SOMETHING FAILS:

### Issue: "Database does not exist"
**Solution:** Create it again
```powershell
docker exec postgres-whatsapp createdb -U postgres whatsapp_agent
```

### Issue: "Could not connect to PostgreSQL"
**Solution:** Restart Docker container
```powershell
docker stop postgres-whatsapp
docker start postgres-whatsapp
```

### Issue: "Alembic reports invalid SQL syntax"
**Solution:** Check if migration file is correct
```powershell
# Review the migration
cat alembic\versions\20260114_001_complete_initial_migration.py
```

### Issue: "Table already exists"
**Solution:** Downgrade first, then upgrade
```powershell
alembic downgrade base
alembic upgrade head
```

### Issue: "Permission denied" on Windows
**Solution:** Run PowerShell as Administrator
```powershell
# Close current PowerShell
# Right-click PowerShell → Run as Administrator
# Then run the commands again
```

## WHAT SHOULD HAPPEN:

1. ✅ Alembic reads the migration file
2. ✅ Alembic connects to PostgreSQL
3. ✅ Alembic creates the schema with all tables
4. ✅ alembic_version table tracks the migration
5. ✅ All 20 tables are now in your database
6. ✅ FastAPI can connect and use these tables
7. ✅ You're ready to use the API!

---

**Run through all these steps and let me know if everything passes!** ✅
