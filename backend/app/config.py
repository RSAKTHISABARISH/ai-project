import os
from typing import List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator

class Settings(BaseSettings):
    PROJECT_NAME: str = "Fix2Runbook"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"
    
    # Environment & Database
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    DATABASE_URL: str = "sqlite:///./fix2runbook.db"
    
    # AI / External Credentials
    LLM_API_KEY: str = ""
    GITHUB_TOKEN: str = ""
    
    # Server & Networking
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    CORS_ORIGINS: Union[List[str], str] = ["*"]
    
    model_config = SettingsConfigDict(env_file=".env", extra="allow")
    
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, str) and v.startswith("["):
            import json
            try:
                return json.loads(v)
            except Exception:
                return ["*"]
        elif isinstance(v, list):
            return v
        return ["*"]

    @property
    def has_llm_key(self) -> bool:
        return bool(self.LLM_API_KEY and self.LLM_API_KEY.strip() and not self.LLM_API_KEY.startswith("your_"))


settings = Settings()
