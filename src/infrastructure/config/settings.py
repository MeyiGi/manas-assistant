"""
src/infrastructure/config/settings.py
=======================================
Single Settings object for the entire platform.
All environment variables declared here — no other module reads os.environ.
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass(frozen=True)
class ServerSettings:
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    cors_origins: list[str] = field(default_factory=lambda: ["*"])


@dataclass(frozen=True)
class DatabaseSettings:
    url: str = "sqlite+aiosqlite:///./manas_platform.db"
    echo: bool = False
    pool_size: int = 10


@dataclass(frozen=True)
class AuthSettings:
    jwt_secret: str = "CHANGE_ME_IN_PRODUCTION"
    token_ttl_minutes: int = 60 * 24


@dataclass(frozen=True)
class TimetableSettings:
    base_url: str = "http://timetable.manas.edu.kg/department-printer"
    start_id: int = 95
    end_id: int = 141
    concurrency: int = 20
    timeout: float = 20.0
    scrape_interval_hours: int = 6


@dataclass(frozen=True)
class NotificationSettings:
    telegram_bot_token: str = ""
    telegram_enabled: bool = False
    email_host: str = "smtp.gmail.com"
    email_port: int = 587
    email_user: str = ""
    email_password: str = ""
    email_enabled: bool = False


@dataclass(frozen=True)
class DocumentSettings:
    llm_provider: str = "ollama"           # "openai" | "ollama"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3"
    storage_backend: str = "local"         # "local" | "s3"
    local_storage_path: str = "./uploads"
    s3_bucket: str = ""
    s3_region: str = ""
    max_file_size_mb: int = 50
    chunk_size: int = 1000
    chunk_overlap: int = 200


@dataclass(frozen=True)
class CafeteriaSettings:
    api_url: str = "https://manas.edu.kg/api/yemek"
    cache_ttl_hours: int = 1


@dataclass(frozen=True)
class SchedulerSettings:
    timetable_scrape_cron: str = "0 */6 * * *"
    assignment_check_cron: str = "*/15 * * * *"
    exam_reminder_cron: str = "*/30 * * * *"
    cafeteria_refresh_cron: str = "0 7 * * *"


@dataclass(frozen=True)
class Settings:
    server: ServerSettings = field(default_factory=ServerSettings)
    database: DatabaseSettings = field(default_factory=DatabaseSettings)
    auth: AuthSettings = field(default_factory=AuthSettings)
    timetable: TimetableSettings = field(default_factory=TimetableSettings)
    notifications: NotificationSettings = field(default_factory=NotificationSettings)
    documents: DocumentSettings = field(default_factory=DocumentSettings)
    cafeteria: CafeteriaSettings = field(default_factory=CafeteriaSettings)
    scheduler: SchedulerSettings = field(default_factory=SchedulerSettings)

    @classmethod
    def from_env(cls) -> "Settings":
        return cls(
            server=ServerSettings(
                host=os.environ.get("SERVER_HOST", "0.0.0.0"),
                port=int(os.environ.get("SERVER_PORT", 8000)),
                debug=os.environ.get("DEBUG", "false").lower() == "true",
            ),
            database=DatabaseSettings(
                url=os.environ.get("DATABASE_URL", "sqlite+aiosqlite:///./manas_platform.db"),
                echo=os.environ.get("DB_ECHO", "false").lower() == "true",
            ),
            auth=AuthSettings(
                jwt_secret=os.environ.get("JWT_SECRET", "CHANGE_ME_IN_PRODUCTION"),
                token_ttl_minutes=int(os.environ.get("TOKEN_TTL_MINUTES", 1440)),
            ),
            timetable=TimetableSettings(
                base_url=os.environ.get("TIMETABLE_BASE_URL", "http://timetable.manas.edu.kg/department-printer"),
                start_id=int(os.environ.get("TIMETABLE_START_ID", 95)),
                end_id=int(os.environ.get("TIMETABLE_END_ID", 141)),
                concurrency=int(os.environ.get("TIMETABLE_CONCURRENCY", 20)),
                timeout=float(os.environ.get("TIMETABLE_TIMEOUT", 20.0)),
            ),
            notifications=NotificationSettings(
                telegram_bot_token=os.environ.get("TELEGRAM_BOT_TOKEN", ""),
                telegram_enabled=os.environ.get("TELEGRAM_ENABLED", "false").lower() == "true",
                email_host=os.environ.get("EMAIL_HOST", "smtp.gmail.com"),
                email_port=int(os.environ.get("EMAIL_PORT", 587)),
                email_user=os.environ.get("EMAIL_USER", ""),
                email_password=os.environ.get("EMAIL_PASSWORD", ""),
                email_enabled=os.environ.get("EMAIL_ENABLED", "false").lower() == "true",
            ),
            documents=DocumentSettings(
                llm_provider=os.environ.get("LLM_PROVIDER", "ollama"),
                openai_api_key=os.environ.get("OPENAI_API_KEY", ""),
                openai_model=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"),
                ollama_base_url=os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434"),
                ollama_model=os.environ.get("OLLAMA_MODEL", "llama3"),
                storage_backend=os.environ.get("STORAGE_BACKEND", "local"),
                local_storage_path=os.environ.get("LOCAL_STORAGE_PATH", "./uploads"),
                s3_bucket=os.environ.get("S3_BUCKET", ""),
                max_file_size_mb=int(os.environ.get("MAX_FILE_SIZE_MB", 50)),
            ),
            cafeteria=CafeteriaSettings(
                api_url=os.environ.get("CAFETERIA_API_URL", "https://manas.edu.kg/api/yemek"),
                cache_ttl_hours=int(os.environ.get("CAFETERIA_CACHE_TTL_HOURS", 1)),
            ),
            scheduler=SchedulerSettings(
                timetable_scrape_cron=os.environ.get("CRON_TIMETABLE", "0 */6 * * *"),
                assignment_check_cron=os.environ.get("CRON_ASSIGNMENTS", "*/15 * * * *"),
                exam_reminder_cron=os.environ.get("CRON_EXAMS", "*/30 * * * *"),
            ),
        )
