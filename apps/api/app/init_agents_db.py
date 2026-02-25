import sys
import os
from sqlalchemy import create_engine
from apps.api.app.core.database import Base
from apps.api.app.core.config import settings
# Import all models to ensure they are registered with Base
from apps.api.app.models import *

def init_db():
    print(f"Connecting to: {settings.SQLALCHEMY_DATABASE_URI}")
    engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)
    
    print("Creating tables if they don't exist...")
    Base.metadata.create_all(bind=engine)
    print("Done!")

if __name__ == "__main__":
    init_db()
