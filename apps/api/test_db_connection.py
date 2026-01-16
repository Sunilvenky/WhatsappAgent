#!/usr/bin/env python3
"""Test database connection with various methods"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
print(f"Testing connection with: {DATABASE_URL[:50]}...")

# Method 1: psycopg2
print("\n1. Testing with psycopg2...")
try:
    import psycopg2
    conn = psycopg2.connect(DATABASE_URL)
    print("   ✅ psycopg2 connection successful!")
    conn.close()
except Exception as e:
    print(f"   ❌ psycopg2 failed: {e}")

# Method 2: SQLAlchemy (what Alembic uses)
print("\n2. Testing with SQLAlchemy...")
try:
    from sqlalchemy import create_engine, text
    engine = create_engine(DATABASE_URL)
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        print("   ✅ SQLAlchemy connection successful!")
except Exception as e:
    print(f"   ❌ SQLAlchemy failed: {e}")

# Method 3: Alembic directly
print("\n3. Testing Alembic migration readiness...")
try:
    from alembic.config import Config
    from alembic import command
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", DATABASE_URL)
    # Check if we can get connection from Alembic
    print("   ✅ Alembic config loaded successfully!")
except Exception as e:
    print(f"   ❌ Alembic config failed: {e}")

print("\nDone!")
