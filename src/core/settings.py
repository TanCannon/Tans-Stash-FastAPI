import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()


class Settings:
    # App
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    BANNER_UPLOAD_PATH: str = os.getenv("BANNER_UPLOAD_PATH")
    NO_OF_POSTS: int = int(os.getenv("NO_OF_POSTS"))

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-me")

    # Admin
    ADMIN_USERNAME: str = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD: str = os.getenv("ADMIN_PASSWORD", "admin")

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL")

    # Pagination
    # POSTS_PER_PAGE: int = int(os.getenv("POSTS_PER_PAGE", 5))


settings = Settings()