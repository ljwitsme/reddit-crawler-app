# import os
# from dotenv import load_dotenv

# load_dotenv()


# class Settings:
#     REDDIT_CLIENT_ID: str = os.getenv("REDDIT_CLIENT_ID", "")
#     REDDIT_CLIENT_SECRET: str = os.getenv("REDDIT_CLIENT_SECRET", "")
#     REDDIT_USER_AGENT: str = os.getenv("REDDIT_USER_AGENT", "reddit-crawler/0.1")
#     DATABASE_URL: str = os.getenv("DATABASE_URL", "")

#     def validate(self) -> None:
#         missing = [
#             k for k in ("REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET", "DATABASE_URL")
#             if not getattr(self, k)
#         ]
#         if missing:
#             raise RuntimeError(f"Missing required env vars: {', '.join(missing)}")


# settings = Settings()
# settings.validate()

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    REDDIT_CLIENT_ID: str = os.getenv("REDDIT_CLIENT_ID", "")
    REDDIT_CLIENT_SECRET: str = os.getenv("REDDIT_CLIENT_SECRET", "")
    REDDIT_USER_AGENT: str = os.getenv("REDDIT_USER_AGENT", "reddit-crawler/0.1")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    USE_MOCK: bool = os.getenv("USE_MOCK", "true").lower() == "true"

    def validate(self) -> None:
        # DATABASE_URL is always required
        if not self.DATABASE_URL:
            raise RuntimeError("Missing required env var: DATABASE_URL")
        # Reddit credentials only required when not using mock
        if not self.USE_MOCK:
            missing = [
                k for k in ("REDDIT_CLIENT_ID", "REDDIT_CLIENT_SECRET")
                if not getattr(self, k)
            ]
            if missing:
                raise RuntimeError(
                    f"Missing Reddit credentials (required when USE_MOCK=false): {', '.join(missing)}"
                )


settings = Settings()
settings.validate()