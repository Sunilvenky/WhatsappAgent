"""v1 API package."""

from fastapi import APIRouter

from .auth import router as auth_router
from .health import router as health_router
from .users import router as users_router
from .contacts import router as contacts_router
from .campaigns import router as campaigns_router
from .conversations import router as conversations_router
from .leads import router as leads_router
from .webhooks import router as webhooks_router
from .whatsapp import router as whatsapp_router
from .ai import router as ai_router
from .analytics import router as analytics_router
from .agents import router as agents_router
# ML routers temporarily disabled - googletrans incompatible with Python 3.13 (missing cgi module)
# from .ml import router as ml_router
# from .training import router as training_router

api_router = APIRouter()

# Include all routers
api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])
api_router.include_router(health_router, prefix="/health", tags=["health"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(contacts_router, prefix="/contacts", tags=["contacts"])
api_router.include_router(campaigns_router, prefix="/campaigns", tags=["campaigns"])
api_router.include_router(conversations_router, prefix="/conversations", tags=["conversations"])
api_router.include_router(leads_router, prefix="/leads", tags=["leads"])
api_router.include_router(webhooks_router, prefix="/webhooks", tags=["webhooks"])
api_router.include_router(whatsapp_router, prefix="/whatsapp", tags=["whatsapp"])
api_router.include_router(agents_router, prefix="/agents", tags=["agents"])
api_router.include_router(ai_router, tags=["ai"])
api_router.include_router(analytics_router, tags=["analytics"])
# ML routers disabled - googletrans incompatible with Python 3.13
# api_router.include_router(ml_router, tags=["machine-learning"])
# api_router.include_router(training_router, tags=["ML Training"])