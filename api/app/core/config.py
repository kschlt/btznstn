"""Application configuration."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Database
    database_url: str = "postgresql+asyncpg://betzenstein:dev_password@localhost:5432/betzenstein_dev"
    db_echo: bool = False

    # Application
    python_env: str = "development"
    log_level: str = "INFO"
    secret_key: str = "your-secret-key-here-generate-with-openssl-rand-hex-32"  # noqa: S105

    # CORS (comma-separated string)
    allowed_origins: str = "http://localhost:3000"

    def get_allowed_origins(self) -> list[str]:
        """Parse comma-separated CORS origins."""
        return [origin.strip() for origin in self.allowed_origins.split(",") if origin.strip()]

    # Rate limiting (BR-012)
    max_bookings_per_day: int = 10
    max_requests_per_hour: int = 30
    max_recovery_requests_per_hour: int = 5

    # Business rules
    max_party_size: int = 10
    future_horizon_months: int = 18
    long_stay_warn_days: int = 7

    # Email (Phase 4)
    resend_api_key: str | None = None


settings = Settings()
