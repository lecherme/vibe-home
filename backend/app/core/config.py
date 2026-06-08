from functools import lru_cache
from typing import Literal, Optional

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    supabase_url: str = Field(..., alias="SUPABASE_URL")
    supabase_key: str = Field(..., alias="SUPABASE_KEY")
    supabase_jwt_secret: Optional[str] = Field(default=None, alias="SUPABASE_JWT_SECRET")
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    llm_provider: Literal["anthropic", "openai", "openai_compatible"] = Field(
        default="anthropic",
        alias="LLM_PROVIDER",
    )
    llm_api_key: Optional[str] = Field(default=None, alias="LLM_API_KEY")
    llm_model: str = Field(default="claude-3-5-haiku-latest", alias="LLM_MODEL")
    llm_base_url: Optional[str] = Field(default=None, alias="LLM_BASE_URL")
    allowed_origins_raw: str = Field(..., alias="ALLOWED_ORIGINS")

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins_raw.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
