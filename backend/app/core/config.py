from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite:///./coach.db"
    secret_key: str = "change-me-in-production"
    access_token_minutes: int = 60 * 24
    llm_provider: str = "gemini"  # "gemini" or "mock"
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"  # set to a current model name
    cors_origins: str = "http://localhost:5173"


settings = Settings()
