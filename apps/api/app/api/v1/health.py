"""
Health check router.
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional

router = APIRouter()


class HealthResponse(BaseModel):
    code: str
    message: str
    data: Optional[dict] = None


@router.get("/health", response_model=HealthResponse)
async def health():
    return {"code": "ok", "message": "healthy", "data": {"status": "ok"}}