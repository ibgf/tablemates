import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings
from pydantic import Field

load_dotenv()  # ⏪ 确保在 Settings 定义之前调用

class Settings(BaseSettings):
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ALGORITHM: str = Field(default="HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=180, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=30, env="REFRESH_TOKEN_EXPIRE_DAYS")

    class Config:
        env_file = ".env"

settings = Settings()

# 可选：为兼容旧代码保留的原写法
DATABASE_URL = os.getenv("DATABASE_URL")


