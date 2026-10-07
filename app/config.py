from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_env: str = "local"
    llm_provider: str = "anthropic"
    llm_api_key: str = ""


settings = Settings()
