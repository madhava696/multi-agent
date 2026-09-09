from typing import List, Literal
from pydantic_settings import BaseSettings,SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Multi Agent Starter Backend"
    app_env: str = "development"
    api_prefix: str = "/api/v1"
    backend_cors_origins: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://192.168.0.247:3000"
    ]

    llm_provider: Literal["ollama", "huggingface"] = "ollama"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.1:8b"

    model_summarization: str = ""
    model_code_generation: str = ""
    model_question_answering: str = ""
    model_reasoning: str = ""

    huggingface_api_key: str = ""
    huggingface_model: str = "mistralai/Mistral-7B-Instruct-v0.3"

    redis_url: str = "redis://172.27.146.212:6379/0"
    redis_ttl_seconds: int = 3600

    elasticsearch_url: str = "http://localhost:9200"
    elasticsearch_index: str = "starter_documents"
    elasticsearch_api_key: str = ""
    elasticsearch_user: str = "elastic"
    elasticsearch_password: str = ""

    langfuse_host: str = "http://localhost:3001"
    langfuse_public_key: str = ""
    langfuse_secret_key: str = ""
    langfuse_env: str = "local"
    langfuse_user_id: str = "local-dev"
    langfuse_enabled: bool = False
    langfuse_base_url: str = "http://localhost:3001"

    auth_secret_key: str = "change-me-in-real-projects"
    auth_algorithm: str = "HS256"
    auth_token_expiry_minutes: int = 120


    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

settings = Settings()
