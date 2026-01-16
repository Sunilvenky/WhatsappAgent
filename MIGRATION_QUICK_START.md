# 🚀 MIGRATION QUICK START

## ONE COMMAND TO RUN EVERYTHING:

```powershell
cd "e:\Sunny React Projects\Whatsapp Agent\apps\api" && powershell -ExecutionPolicy Bypass -File run_migrations.ps1
```

---

## WHAT WILL HAPPEN:

1. ✅ Check PostgreSQL is running (starts if not)
2. ✅ Verify .env file exists
3. ✅ Activate Python virtual environment
4. ✅ Install required packages
5. ✅ **DOWNGRADE** old migrations (if any)
6. ✅ **RUN** the complete migration with 20 tables
7. ✅ Verify all tables were created
8. ✅ Show status report

---

## EXPECTED RESULT:

```
🎉 ALL CHECKS PASSED! Your database is ready to use.

✅ PostgreSQL Running
✅ .env File Exists
✅ Migration Applied (20260114_001)
✅ 20 Tables Created

Next steps:
1. Start FastAPI: python -m uvicorn app.main:app --reload
2. Visit: http://localhost:8000/docs
3. Start WhatsApp Gateway: cd ../whatsapp-gateway && npm start
4. Start React UI: cd ../ui && npm run dev
```

---

## MANUAL STEPS (If script doesn't work):

```powershell
# 1. Navigate to API folder
cd "e:\Sunny React Projects\Whatsapp Agent\apps\api"

# 2. Activate virtual environment
.\venv\Scripts\Activate.ps1

# 3. Downgrade any old migrations
alembic downgrade base

# 4. Run the new complete migration
alembic upgrade head

# 5. Verify
alembic current

# 6. Check tables
docker exec postgres-whatsapp psql -U postgres -d whatsapp_agent -c "\dt"
```

---

## VERIFY AFTER MIGRATION:

```powershell
# Should show: 20260114_001 (head)
alembic current

# Should show 20+ tables
docker exec postgres-whatsapp psql -U postgres -d whatsapp_agent -c "SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename;"
```

---

## THEN START THE FULL STACK:

```powershell
# Terminal 1: FastAPI
cd "e:\Sunny React Projects\Whatsapp Agent\apps\api"
python -m uvicorn app.main:app --reload

# Terminal 2: WhatsApp Gateway
cd "e:\Sunny React Projects\Whatsapp Agent\apps\whatsapp-gateway"
npm start

# Terminal 3: React UI
cd "e:\Sunny React Projects\Whatsapp Agent\apps\ui"
npm run dev
```

---

## THAT'S IT! 🎉

Your WhatsApp API with **20 fully-designed database tables** is ready!

Visit: http://localhost:8000/docs to see all endpoints
