import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    environment: str = os.getenv("ENVIRONMENT", "development").strip().lower()
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    groq_model: str = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
    data_gov_api_key: str = os.getenv("DATA_GOV_API_KEY", "")
    openweather_api_key: str = os.getenv("OPENWEATHER_API_KEY", "")
    frontend_origins: tuple[str, ...] = tuple(
        origin.strip()
        for origin in os.getenv(
            "FRONTEND_ORIGINS",
            "" if environment == "production" else "http://localhost:5173,http://127.0.0.1:5173",
        ).split(",")
        if origin.strip()
    )
    groq_timeout_seconds: int = int(os.getenv("GROQ_TIMEOUT_SECONDS", "12"))
    external_api_timeout_seconds: int = int(os.getenv("EXTERNAL_API_TIMEOUT_SECONDS", "15"))
    rate_limit_window_seconds: int = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))
    chat_rate_limit_requests: int = int(os.getenv("CHAT_RATE_LIMIT_REQUESTS", "30"))
    external_api_rate_limit_requests: int = int(os.getenv("EXTERNAL_API_RATE_LIMIT_REQUESTS", "60"))


settings = Settings()
