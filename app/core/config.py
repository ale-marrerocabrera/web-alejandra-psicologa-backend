from functools import lru_cache

from pydantic import EmailStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    database_url: str = "sqlite:///./data/alejandra.db"
    frontend_origins: str = "http://localhost:3000"
    contact_rate_limit: int = 5
    contact_rate_window_seconds: int = 3600
    admin_email: EmailStr | None = None
    admin_password: str | None = None
    session_duration_hours: int = 8
    session_cookie_secure: bool = False

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @field_validator("admin_email", "admin_password", mode="before")
    @classmethod
    def empty_admin_credentials_are_unset(cls, value: str | None) -> str | None:
        return None if isinstance(value, str) and not value.strip() else value

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.frontend_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
