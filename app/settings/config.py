import os
import typing
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent.parent.parent / ".env", env_file_encoding="utf-8", extra="ignore"
    )

    VERSION: str = "0.1.0"
    APP_TITLE: str = "Vue FastAPI Admin"
    PROJECT_NAME: str = "Vue FastAPI Admin"
    APP_DESCRIPTION: str = "Description"

    CORS_ORIGINS: typing.List = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: typing.List = ["*"]
    CORS_ALLOW_HEADERS: typing.List = ["*"]

    DEBUG: bool = True

    PROJECT_ROOT: str = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    BASE_DIR: str = os.path.abspath(os.path.join(PROJECT_ROOT, os.pardir))
    LOGS_ROOT: str = os.path.join(BASE_DIR, "app/logs")
    SECRET_KEY: str = "3488a63e1765035d386f05409663f55c83bfae3b3c61a932744b20ad14244dcf"  # openssl rand -hex 32
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", 30))  # 20 minute
    JWT_REFRESH_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_MINUTES", 600))  # 600 minutes
    DB_TYPE: str = os.getenv("DB_TYPE", "sqlite")

    # Redis配置
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
    REDIS_DB: int = int(os.getenv("REDIS_DB", 8))
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", "")

    DB_CONNECTIONS: dict = {
        "sqlite": {
            "engine": "tortoise.backends.sqlite",
            "credentials": {"file_path": f"{BASE_DIR}/db.sqlite3"},  # Path to SQLite database file
        },
        # MySQL/MariaDB configuration
        # Install with: tortoise-orm[asyncmy]
        "mysql": {
            "engine": "tortoise.backends.mysql",
            "credentials": {
                "host": os.getenv("DB_HOST", "10.1.20.9"),  # Database host address
                "port": int(os.getenv("DB_PORT", 3306)),  # Database port
                "user": os.getenv("DB_USER", "root"),  # Database username
                "password": os.getenv("DB_PASSWORD", "mysql_fxQZsy"),  # Database password
                "database": os.getenv("DB_NAME", "fastapi"),  # Database name
            },
        },
        # PostgreSQL configuration
        # Install with: tortoise-orm[asyncpg]
        # "postgres": {
        #     "engine": "tortoise.backends.asyncpg",
        #     "credentials": {
        #         "host": "localhost",  # Database host address
        #         "port": 5432,  # Database port
        #         "user": "yourusername",  # Database username
        #         "password": "yourpassword",  # Database password
        #         "database": "yourdatabase",  # Database name
        #     },
        # },
        # MSSQL/Oracle configuration
        # Install with: tortoise-orm[asyncodbc]
        # "oracle": {
        #     "engine": "tortoise.backends.asyncodbc",
        #     "credentials": {
        #         "host": "localhost",  # Database host address
        #         "port": 1433,  # Database port
        #         "user": "yourusername",  # Database username
        #         "password": "yourpassword",  # Database password
        #         "database": "yourdatabase",  # Database name
        #     },
        # },
        # SQLServer configuration
        # Install with: tortoise-orm[asyncodbc]
        # "sqlserver": {
        #     "engine": "tortoise.backends.asyncodbc",
        #     "credentials": {
        #         "host": "localhost",  # Database host address
        #         "port": 1433,  # Database port
        #         "user": "yourusername",  # Database username
        #         "password": "yourpassword",  # Database password
        #         "database": "yourdatabase",  # Database name
        #     },
        # },
    }
    TORTOISE_ORM: dict = {
        "connections": {
            "default": DB_CONNECTIONS[DB_TYPE],
        },
        "apps": {
            "models": {
                "models": ["app.models", "aerich.models"],
                "default_connection": "default",
            },
        },
        "use_tz": False,  # Whether to use timezone-aware datetimes
        "timezone": "Asia/Shanghai",  # Timezone setting
    }
    DATETIME_FORMAT: str = "%Y-%m-%d %H:%M:%S"


settings = Settings()
