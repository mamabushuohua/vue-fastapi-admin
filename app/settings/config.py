import os
import typing

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    VERSION: str = "0.1.0"
    APP_TITLE: str = "FastAPI Admin"
    PROJECT_NAME: str = "FastAPI-Admin"
    APP_DESCRIPTION: str = "Description"

    CORS_ORIGINS: typing.List = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: typing.List = ["*"]
    CORS_ALLOW_HEADERS: typing.List = ["*"]

    DEBUG: bool = os.getenv("DEBUG", True)

    PROJECT_ROOT: str = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    BASE_DIR: str = os.path.abspath(os.path.join(PROJECT_ROOT, os.pardir))

    # static files
    STATIC_ROOT: str = os.path.join(PROJECT_ROOT, "static")
    STATIC_URL: str = "/api/static"
    if not os.path.exists(STATIC_ROOT):
        os.makedirs(STATIC_ROOT)

    BASE_DB_DIR: str = os.path.abspath(os.path.join(BASE_DIR, "db"))
    if not os.path.exists(BASE_DB_DIR):
        os.makedirs(BASE_DB_DIR)
    LOGS_ROOT: str = os.path.join(BASE_DIR, "logs")
    if not os.path.exists(LOGS_ROOT):
        os.makedirs(LOGS_ROOT)
    SECRET_KEY: str = "690aab8b530e194045a77bb67aff1f6f34546bae772837ec7a3a5d7f456bcbf3"  # openssl rand -hex 32
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 day

    # DB CONFIG
    DB_TYPE: str = os.getenv("DB_TYPE", "sqlite")
    DB_CONNECTIONS: dict = {
        "sqlite": {
            "engine": "tortoise.backends.sqlite",
            "credentials": {"file_path": f"{BASE_DB_DIR}/db.sqlite3"},  # Path to SQLite database file
        },
        # MySQL/MariaDB configuration
        # Install with: tortoise-orm[asyncmy]
        "mysql": {
            "engine": "tortoise.backends.mysql",
            "credentials": {
                "host": os.getenv("DB_HOST", "localhost"),  # Database host address
                "port": int(os.getenv("DB_PORT", 3306)),  # Database port
                "user": os.getenv("DB_USER", "yourusername"),  # Database username
                "password": os.getenv("DB_PASSWORD", "yourpassword"),  # Database password
                "database": os.getenv("DB_NAME", "yourdatabase"),  # Database name
            },
        },
        # SQLite configuration
        # "sqlite": {
        #     "engine": "tortoise.backends.sqlite",
        #     "credentials": {"file_path": f"{BASE_DB_DIR}/db.sqlite3"},  # Path to SQLite database file
        # },
        # MySQL/MariaDB configuration
        # Install with: tortoise-orm[asyncmy]
        # "mysql": {
        #     "engine": "tortoise.backends.mysql",
        #     "credentials": {
        #         "host": os.getenv("DB_HOST", "localhost"),  # Database host address
        #         "port": int(os.getenv("DB_PORT", 3306)),  # Database port
        #         "user": os.getenv("DB_USER", "yourusername"),  # Database username
        #         "password": os.getenv("DB_PASSWORD", "yourpassword"),  # Database password
        #         "database": os.getenv("DB_NAME", "yourdatabase"),  # Database name
        #     },
        # },
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
        # "mysql": DB_CONNECTIONS["mysql"],
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

    API_KEY: str = os.getenv("API_KEY", "yourapikey")

    # gitlab 配置
    GITLAB_API_URL: str = os.getenv("GITLAB_API_URL", "https://gitlab.com/api/v4")
    GITLAB_PRIVATE_TOKEN: str = os.getenv("GITLAB_PRIVATE_TOKEN", "yourtoken")


settings = Settings()
