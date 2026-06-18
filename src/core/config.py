from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    APP_ENV: str = Field(default="development", env="APP_ENV")
    PROJECT_NAME: str = Field(default="AI Inference Gateway", env="PROJECT_NAME")
    LOG_LEVEL: str = Field(default="info", env="LOG_LEVEL")
    
    REDIS_URL: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    
    OPENAI_API_KEY: str = Field(default="sk-mock-key", env="OPENAI_API_KEY")
    UPSTREAM_LLM_URL: str = Field(default="https://api.openai.com/v1/chat/completions", env="UPSTREAM_LLM_URL")
    
    SEMANTIC_CACHE_THRESHOLD: float = Field(default=0.92, env="SEMANTIC_CACHE_THRESHOLD")
    GLOBAL_RATE_LIMIT_PER_MIN: int = Field(default=60, env="GLOBAL_RATE_LIMIT_PER_MIN")

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()