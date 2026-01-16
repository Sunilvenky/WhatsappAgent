#!/usr/bin/env pwsh

# ===== AUTOMATIC MIGRATION SCRIPT =====
# This script runs all migration steps automatically
# Usage: .\run_migrations.ps1

Write-Host "🚀 Starting Migration Process..." -ForegroundColor Cyan
Write-Host ""

# ===== STEP 1: CHECK POSTGRESQL =====
Write-Host "📦 Step 1: Checking PostgreSQL..." -ForegroundColor Yellow
$pgRunning = docker ps | Select-String "postgres-whatsapp"
if ($pgRunning) {
    Write-Host "✅ PostgreSQL is running" -ForegroundColor Green
} else {
    Write-Host "❌ PostgreSQL is NOT running" -ForegroundColor Red
    Write-Host "   Starting PostgreSQL Docker container..." -ForegroundColor Yellow
    docker start postgres-whatsapp
    Start-Sleep -Seconds 3
    Write-Host "✅ PostgreSQL started" -ForegroundColor Green
}
Write-Host ""

# ===== STEP 2: CHECK .ENV FILE =====
Write-Host "📋 Step 2: Checking .env file..." -ForegroundColor Yellow
if (Test-Path ".env") {
    Write-Host "✅ .env file exists" -ForegroundColor Green
    $dbUrl = (Select-String "DATABASE_URL" .env).Line
    Write-Host "   $dbUrl" -ForegroundColor Gray
} else {
    Write-Host "❌ .env file NOT found" -ForegroundColor Red
    exit 1
}
Write-Host ""

# ===== STEP 3: ACTIVATE VENV =====
Write-Host "🐍 Step 3: Activating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv\Scripts\Activate.ps1") {
    & "venv\Scripts\Activate.ps1"
    Write-Host "✅ Virtual environment activated" -ForegroundColor Green
} else {
    Write-Host "❌ Virtual environment not found" -ForegroundColor Red
    Write-Host "   Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    & "venv\Scripts\Activate.ps1"
    Write-Host "✅ Virtual environment created and activated" -ForegroundColor Green
}
Write-Host ""

# ===== STEP 4: INSTALL DEPENDENCIES =====
Write-Host "📚 Step 4: Installing dependencies..." -ForegroundColor Yellow
pip install -q alembic sqlalchemy psycopg2-binary 2>$null
Write-Host "✅ Dependencies installed" -ForegroundColor Green
Write-Host ""

# ===== STEP 5: CHECK CURRENT MIGRATION STATUS =====
Write-Host "🔍 Step 5: Checking current migration status..." -ForegroundColor Yellow
$currentMigration = alembic current 2>&1
Write-Host "   Current: $currentMigration" -ForegroundColor Gray
Write-Host ""

# ===== STEP 6: DOWNGRADE EXISTING MIGRATIONS =====
Write-Host "⬇️  Step 6: Downgrading existing migrations..." -ForegroundColor Yellow
alembic downgrade base 2>&1 | Select-String -Pattern "Downgrading|already at", "INFO" -ErrorAction SilentlyContinue | ForEach-Object { Write-Host "   $_" -ForegroundColor Gray }
Write-Host "✅ Downgrades complete" -ForegroundColor Green
Write-Host ""

# ===== STEP 7: RUN NEW MIGRATION =====
Write-Host "⬆️  Step 7: Running new complete migration..." -ForegroundColor Yellow
$migrationOutput = alembic upgrade head 2>&1
Write-Host $migrationOutput | Select-String "Running upgrade|success|complete" -ErrorAction SilentlyContinue | ForEach-Object { Write-Host "   $_" -ForegroundColor Gray }
Write-Host "✅ Migration completed" -ForegroundColor Green
Write-Host ""

# ===== STEP 8: VERIFY MIGRATION STATUS =====
Write-Host "✔️  Step 8: Verifying migration status..." -ForegroundColor Yellow
$currentMigration = alembic current 2>&1
Write-Host "   Current: $currentMigration" -ForegroundColor Green
Write-Host ""

# ===== STEP 9: COUNT TABLES =====
Write-Host "📊 Step 9: Counting database tables..." -ForegroundColor Yellow
$tableCount = docker exec postgres-whatsapp psql -U postgres -d whatsapp_agent -c "SELECT COUNT(*) FROM pg_tables WHERE schemaname='public';" 2>&1 | Select-String -Pattern "^\s+\d+" | ForEach-Object { $_ -replace '\s+', '' }
Write-Host "   Total tables created: $tableCount" -ForegroundColor Green
Write-Host ""

# ===== STEP 10: LIST ALL TABLES =====
Write-Host "📋 Step 10: All tables in database:" -ForegroundColor Yellow
$tables = docker exec postgres-whatsapp psql -U postgres -d whatsapp_agent -c "SELECT tablename FROM pg_tables WHERE schemaname='public' ORDER BY tablename;" 2>&1 | Select-String "^\s+[a-z_]"
if ($tables) {
    $tables | ForEach-Object {
        $tableName = $_ -replace '\s+', ''
        Write-Host "   ✅ $tableName" -ForegroundColor Green
    }
} else {
    Write-Host "   ❌ No tables found!" -ForegroundColor Red
}
Write-Host ""

# ===== FINAL CHECK =====
Write-Host "🎯 FINAL VERIFICATION:" -ForegroundColor Cyan
$finalCheck = @{
    "PostgreSQL Running" = $pgRunning -ne $null
    ".env File Exists" = (Test-Path ".env")
    "Migration Applied" = $currentMigration -like "*20260114_001*"
    "Tables Created" = [int]$tableCount -gt 0
}

$allPass = $true
foreach ($check in $finalCheck.GetEnumerator()) {
    if ($check.Value) {
        Write-Host "✅ $($check.Name)" -ForegroundColor Green
    } else {
        Write-Host "❌ $($check.Name)" -ForegroundColor Red
        $allPass = $false
    }
}
Write-Host ""

if ($allPass) {
    Write-Host "🎉 ALL CHECKS PASSED! Your database is ready to use." -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "1. Start FastAPI: python -m uvicorn app.main:app --reload" -ForegroundColor Gray
    Write-Host "2. Visit: http://localhost:8000/docs" -ForegroundColor Gray
    Write-Host "3. Start WhatsApp Gateway: cd ..\whatsapp-gateway && npm start" -ForegroundColor Gray
    Write-Host "4. Start React UI: cd ..\ui && npm run dev" -ForegroundColor Gray
} else {
    Write-Host "⚠️  Some checks failed. Review the output above." -ForegroundColor Red
    exit 1
}
