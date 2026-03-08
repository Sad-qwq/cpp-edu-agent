
from pathlib import Path

from pydantic_settings import BaseSettings


BACKEND_ENV_FILE = Path(__file__).resolve().parents[2] / ".env"

class Settings(BaseSettings):
    PROJECT_NAME: str = "C++ Education Agent"
    API_V1_STR: str = "/api/v1"
    
    # 数据库配置 (使用 Docker Compose 中的配置)
    POSTGRES_USER: str = "edu_admin"
    POSTGRES_PASSWORD: str = "edu_password_123"
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: str = "5432"
    POSTGRES_DB: str = "edu_pilot_db"
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    # JWT 安全配置
    SECRET_KEY: str = "CHANGE_THIS_IN_PRODUCTION_SECRET_KEY_123456" # 生产环境请修改
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7天有效期

    # AI 配置
    AI_PROVIDER: str = "openai-compatible"
    AI_BASE_URL: str = "https://api.openai.com/v1"
    AI_API_KEY: str = ""
    AI_MODEL_NAME: str = ""
    AI_EMBEDDING_MODEL: str = ""
    AI_ENABLE_REMOTE_GENERATION: bool = True
    
    class Config:
        env_file = str(BACKEND_ENV_FILE)

settings = Settings()
