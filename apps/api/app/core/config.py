"""
Application config using pydantic BaseSettings.
"""
from pydantic import AnyHttpUrl, ConfigDict
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = ConfigDict(env_file=".env")
    
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 3000
    DATABASE_URL: str = "postgresql://postgres:postgres@postgres:5432/whatsapp_agent"
    REDIS_URL: str = "redis://redis:6379/0"
    LLM_STUB_URL: AnyHttpUrl = "http://llm-stub:4000/v1/complete"
    SECRET_KEY: str = "change-me-in-prod"
    
    # JWT settings
    JWT_SECRET_KEY: str = "your-jwt-secret-key-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database settings
    DATABASE_ECHO: bool = False
    
    # WhatsApp Gateway settings
    WHATSAPP_GATEWAY_URL: str = "http://whatsapp-gateway:3001"
    WHATSAPP_GATEWAY_API_KEY: str = "your-whatsapp-gateway-api-key"
    WHATSAPP_WEBHOOK_SECRET: str = "your-webhook-secret-key"
    
    # Celery settings
    CELERY_BROKER_URL: str = "redis://redis:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://redis:6379/0"
    
    # AI/LLM settings
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    LLM_PROVIDER: str = "openai"  # openai, anthropic, ollama
    LLM_MODEL: str = "gpt-4-turbo-preview"
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 1000
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    
    # Campaign execution settings
    MAX_MESSAGES_PER_HOUR: int = 100
    MAX_MESSAGES_PER_DAY: int = 1000
    MESSAGE_DELAY_MIN: int = 2
    MESSAGE_DELAY_MAX: int = 5
    WARMUP_ENABLED: bool = True
    WARMUP_DAYS: int = 14
    
    # AI Feature toggles
    AI_MESSAGE_REWRITING_ENABLED: bool = True
    AI_REPLY_CLASSIFICATION_ENABLED: bool = True
    AI_BAN_RISK_DETECTION_ENABLED: bool = True
    AI_LEAD_SCORING_ENABLED: bool = True


settings = Settings()