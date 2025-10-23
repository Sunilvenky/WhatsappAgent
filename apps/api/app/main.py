"""
FastAPI application bootstrap for WhatsApp Agent API.
Run: python -m apps.api.app.main
"""
import uvicorn
from fastapi import FastAPI
from apps.api.app.api.v1 import api_router
from apps.api.app.core.config import settings

# FastAPI app with OpenAPI documentation
app = FastAPI(
    title="WhatsApp Agent API",
    description="API-first Smart WhatsApp Marketing Agent with comprehensive contact, campaign, conversation, and lead management",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Include all API routes
app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["root"])
def root():
    """Root endpoint."""
    return {
        "message": "WhatsApp Agent API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health"
    }


@app.get("/metrics", tags=["metrics"])
def metrics():
    """Minimal Prometheus text format placeholder."""
    return "# HELP whatsapp_agent_up 1 if up\nwhatsapp_agent_up 1\n"


if __name__ == "__main__":
    uvicorn.run("apps.api.app.main:app", host=settings.API_HOST, port=int(settings.API_PORT), reload=True)