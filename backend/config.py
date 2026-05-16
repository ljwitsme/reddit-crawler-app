import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    REDDIT_CLIENT_ID: str = os.getenv("REDDIT_CLIENT_ID", "")
    REDDIT_CLIENT_SECRET: str = os.getenv("REDDIT_CLIENT_SECRET", "")
    REDDIT_USER_AGENT: str = os.getenv("REDDIT_USER_AGENT", "reddit-crawler/0.1")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")

    def validate(self) -> None:
        missing = [
            k for k in ("REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET", "DATABASE_URL")
            if not getattr(self, k)
        ]
        if missing:
            raise RuntimeError(f"Missing required env vars: {', '.join(missing)}")


settings = Settings()
settings.validate()