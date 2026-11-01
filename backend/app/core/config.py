import os
from typing import List, Union, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application Configuration
    PROJECT_NAME: str = "CampusConnect LPU AI Assistant"
    VERSION: str = "2.0.0"
    API_V1_STR: str = "/api/v1"
    APP_ENV: str = Field(default="development", validation_alias="APP_ENV")
    LOG_LEVEL: str = Field(default="INFO", validation_alias="LOG_LEVEL")

    # Database Configuration (PostgreSQL / SQLite fallback)
    DATABASE_URL: str = Field(
        default="sqlite+aiosqlite:///./campusconnect.db",
        validation_alias="DATABASE_URL"
    )
    DATABASE_DIRECT_URL: Optional[str] = Field(
        default=None,
        validation_alias="DATABASE_DIRECT_URL"
    )
    NEON_DATABASE_URL: Optional[str] = Field(
        default=None,
        validation_alias="NEON_DATABASE_URL"
    )
    NEON_DATABASE_DIRECT_URL: Optional[str] = Field(
        default=None,
        validation_alias="NEON_DATABASE_DIRECT_URL"
    )

    # Redis Cloud Configuration
    REDIS_API_ACCOUNT_KEY: Optional[str] = Field(
        default=None,
        validation_alias="REDIS_API_ACCOUNT_KEY"
    )

    # Gemini AI Configuration (Google Gen AI SDK)
    GEMINI_API_KEY: str = Field(default="", validation_alias="GEMINI_API_KEY")
    GEMINI_API_KEY_SECONDARY: str = Field(default="", validation_alias="GEMINI_API_KEY_SECONDARY")
    GEMINI_MODEL: str = Field(default="gemini-3.5-flash-lite", validation_alias="GEMINI_MODEL")
    GEMINI_MAX_OUTPUT_TOKENS: int = Field(default=1024, validation_alias="GEMINI_MAX_OUTPUT_TOKENS")
    GEMINI_TEMPERATURE: float = Field(default=0.2, validation_alias="GEMINI_TEMPERATURE")
    GEMINI_TIMEOUT_SECONDS: int = Field(default=30, validation_alias="GEMINI_TIMEOUT_SECONDS")
    GEMINI_MAX_RETRIES: int = Field(default=2, validation_alias="GEMINI_MAX_RETRIES")

    # Multi-Provider LLM Gateway Configuration
    DEFAULT_LLM_PROVIDER: str = Field(default="gemini", validation_alias="DEFAULT_LLM_PROVIDER")
    ROUTER_SELECTION_STRATEGY: str = Field(default="adaptive", validation_alias="ROUTER_SELECTION_STRATEGY")
    
    # OpenRouter Provider
    OPENROUTER_API_KEY: str = Field(default="", validation_alias="OPENROUTER_API_KEY")
    OPENROUTER_MODEL: str = Field(default="inclusionai/ling-3.2-flash:free", validation_alias="OPENROUTER_MODEL")
    OPENROUTER_BASE_URL: str = Field(default="https://openrouter.ai/api/v1", validation_alias="OPENROUTER_BASE_URL")
    
    # Groq High-Speed Inference Provider
    GROQ_API_KEY: str = Field(default="", validation_alias="GROQ_API_KEY")
    GROQ_MODEL: str = Field(default="llama-3.3-70b-versatile", validation_alias="GROQ_MODEL")
    GROQ_BASE_URL: str = Field(default="https://api.groq.com/openai/v1", validation_alias="GROQ_BASE_URL")

    # BazaarLink AI Provider
    BAZAARLINK_API_KEY: str = Field(default="", validation_alias="BAZAARLINK_API_KEY")
    BAZAARLINK_MODEL: str = Field(default="qwen/qwen3.7-flash:free", validation_alias="BAZAARLINK_MODEL")
    BAZAARLINK_BASE_URL: str = Field(default="https://api.bazaarlink.ai/v1", validation_alias="BAZAARLINK_BASE_URL")

    # Pekpik LLM Provider (DeepSeek Flash & GPT Tokens)
    PEKPIK_DEEPSEEK_API_KEY: str = Field(default="", validation_alias="PEKPIK_DEEPSEEK_API_KEY")
    PEKPIK_GPT_API_KEY: str = Field(default="", validation_alias="PEKPIK_GPT_API_KEY")
    PEKPIK_MODEL: str = Field(default="deepseek-v4-1-flash-1017", validation_alias="PEKPIK_MODEL")
    PEKPIK_BASE_URL: str = Field(default="https://aiapiv2.pekpik.com/v1", validation_alias="PEKPIK_BASE_URL")

    # Aion Labs Provider
    AIONLABS_API_KEY: str = Field(default="", validation_alias="AIONLABS_API_KEY")
    AIONLABS_BASE_URL: str = Field(default="https://api.aionlabs.ai/v1", validation_alias="AIONLABS_BASE_URL")

    # Cohere Provider
    COHERE_API_KEY: str = Field(default="", validation_alias="COHERE_API_KEY")
    COHERE_MODEL: str = Field(default="command-a-03-2025", validation_alias="COHERE_MODEL")
    COHERE_BASE_URL: str = Field(default="https://api.cohere.com/v2", validation_alias="COHERE_BASE_URL")
    
    # Mistral AI Provider
    MISTRAL_API_KEY: str = Field(default="", validation_alias="MISTRAL_API_KEY")
    MISTRAL_MODEL: str = Field(default="mistral-small-latest", validation_alias="MISTRAL_MODEL")
    MISTRAL_BASE_URL: str = Field(default="https://api.mistral.ai/v1", validation_alias="MISTRAL_BASE_URL")
    
    # xAI Grok Provider
    XAI_API_KEY: str = Field(default="", validation_alias="XAI_API_KEY")
    XAI_MODEL: str = Field(default="grok-beta", validation_alias="XAI_MODEL")
    XAI_BASE_URL: str = Field(default="https://api.x.ai/v1", validation_alias="XAI_BASE_URL")
    
    # Generic OpenAI-Compatible Provider
    OPENAI_API_KEY: str = Field(default="", validation_alias="OPENAI_API_KEY")
    OPENAI_MODEL: str = Field(default="gpt-4o-mini", validation_alias="OPENAI_MODEL")
    OPENAI_BASE_URL: str = Field(default="https://api.openai.com/v1", validation_alias="OPENAI_BASE_URL")

    # Live Web Research Configuration
    WEB_RESEARCH_ENABLED: bool = Field(default=True, validation_alias="WEB_RESEARCH_ENABLED")
    WEB_RESEARCH_MAX_RESULTS: int = Field(default=3, validation_alias="WEB_RESEARCH_MAX_RESULTS")

    # Hugging Face Configuration (Serverless Inference & 384-d Embeddings)
    HF_TOKEN: str = Field(default="", validation_alias="HF_TOKEN")
    HF_TOKEN_READ: str = Field(default="", validation_alias="HF_TOKEN_READ")
    HF_TOKEN_WRITE: str = Field(default="", validation_alias="HF_TOKEN_WRITE")
    HF_EMBEDDING_MODEL: str = Field(default="BAAI/bge-small-en-v1.5", validation_alias="HF_EMBEDDING_MODEL")
    HF_EMBEDDING_DIMENSION: int = Field(default=384, validation_alias="HF_EMBEDDING_DIMENSION")

    # Security & JWT for Admin Portal
    JWT_SECRET_KEY: str = Field(
        default="campusconnect_secret_key_change_in_production_32char_min",
        validation_alias="JWT_SECRET_KEY"
    )
    JWT_ALGORITHM: str = Field(default="HS256", validation_alias="JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=480, validation_alias="ACCESS_TOKEN_EXPIRE_MINUTES")

    # Voice AI (Audio Transcription & Speech Synthesis)
    ELEVENLABS_API_KEY: str = Field(default="", validation_alias="ELEVENLABS_API_KEY")
    DEEPGRAM_API_KEY: str = Field(default="", validation_alias="DEEPGRAM_API_KEY")

    # Career & Student Opportunities API
    STARTUP_JOBS_API_KEY: str = Field(default="", validation_alias="STARTUP_JOBS_API_KEY")

    # Geo & Location Intelligence (Campus & Local Phagwara/Jalandhar)
    GEOAPIFY_API_KEY: str = Field(default="", validation_alias="GEOAPIFY_API_KEY")

    # Web Scraping & Crawling
    FIRECRAWL_API_KEY: str = Field(default="", validation_alias="FIRECRAWL_API_KEY")
    UPSCRAPE_API_KEY: str = Field(default="", validation_alias="UPSCRAPE_API_KEY")

    # Neural Search & Reranking (Jina AI)
    JINA_API_KEY: str = Field(default="", validation_alias="JINA_API_KEY")

    # Live Web Intelligence & Research (Tavily & NewsAPI)
    TAVILY_API_KEY: str = Field(default="", validation_alias="TAVILY_API_KEY")
    NEWS_API_KEY: str = Field(default="", validation_alias="NEWS_API_KEY")

    # Weather API (Open-Meteo - No Key Required)
    LPU_LATITUDE: float = Field(default=31.2460, validation_alias="LPU_LATITUDE")
    LPU_LONGITUDE: float = Field(default=75.7047, validation_alias="LPU_LONGITUDE")
    OPEN_METEO_BASE_URL: str = Field(default="https://api.open-meteo.com/v1/forecast", validation_alias="OPEN_METEO_BASE_URL")

    # Initial Admin Seed
    ADMIN_DEFAULT_USERNAME: str = Field(default="admin", validation_alias="ADMIN_DEFAULT_USERNAME")
    ADMIN_DEFAULT_EMAIL: str = Field(default="admin@lpu.co.in", validation_alias="ADMIN_DEFAULT_EMAIL")
    ADMIN_DEFAULT_PASSWORD: str = Field(default="CampusAdmin@2026", validation_alias="ADMIN_DEFAULT_PASSWORD")

    # CORS
    CORS_ORIGINS: Union[str, List[str]] = Field(
        default="http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173",
        validation_alias="CORS_ORIGINS"
    )

    # Rate Limiting & Quota Guards
    MAX_REQUESTS_PER_MINUTE_PER_SESSION: int = Field(default=20, validation_alias="MAX_REQUESTS_PER_MINUTE_PER_SESSION")
    MAX_DAILY_QUOTA_REQUESTS: int = Field(default=1500, validation_alias="MAX_DAILY_QUOTA_REQUESTS")

    # RAG Weights & Confidence Thresholds
    KEYWORD_WEIGHT: float = 0.35
    TFIDF_WEIGHT: float = 0.25
    SEMANTIC_WEIGHT: float = 0.40
    CONFIDENCE_HIGH_THRESHOLD: float = 0.70
    CONFIDENCE_MEDIUM_THRESHOLD: float = 0.45
    CONFIDENCE_LOW_THRESHOLD: float = 0.30

    @field_validator("CORS_ORIGINS", mode="after")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    model_config = SettingsConfigDict(
        env_file=(
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), ".env"),
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env"),
            ".env",
        ),
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()

