from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "DocGenerator"
    APP_ENV: str = "development"
    DEBUG: bool = True
    API_PREFIX: str = "/api/v1"

    # MongoDB Atlas
    MONGODB_URL: str = ""
    MONGODB_DB_NAME: str = "docgen"
    DISABLE_MONGODB: bool = False

    # Hugging Face
    HUGGINGFACE_API_KEY: str = ""
    TEXT_GENERATION_MODEL: str = "meta-llama/Llama-3.2-3B-Instruct"
    IMAGE_GENERATION_MODEL: str = "black-forest-labs/FLUX.1-schnell"

    # File Storage
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 5242880  # 5MB
    ALLOWED_IMAGE_FORMATS: str = "png,jpg,jpeg,svg"

    # PDF Generation
    PDF_OUTPUT_DIR: str = "./generated_pdfs"
    PDF_DPI: int = 300

    # API Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 10

    # CORS
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173"

    # Authentication / JWT
    JWT_SECRET_KEY: str = "your-secret-key-here-change-in-production"
    JWT_REFRESH_SECRET_KEY: str = "your-refresh-secret-key-here-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  # 1 hour
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30  # 30 days

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        # Allow extra fields from environment that aren't in .env file
        extra = "ignore"

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    @property
    def allowed_formats_list(self) -> List[str]:
        return [fmt.strip() for fmt in self.ALLOWED_IMAGE_FORMATS.split(",")]


settings = Settings()
