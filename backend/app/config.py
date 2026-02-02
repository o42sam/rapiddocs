from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "RapidDocs"
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

    # Google Gemini
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "models/gemini-2.0-flash"

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
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173,http://localhost:5174"
    FRONTEND_URL: str = "http://localhost:5174"  # Frontend base URL for OAuth redirects

    # Authentication / JWT
    SECRET_KEY: str = "your-secret-key-here-change-in-production"  # Used for admin JWT
    ALGORITHM: str = "HS256"  # Used for admin JWT
    JWT_SECRET_KEY: str = "your-secret-key-here-change-in-production"
    JWT_REFRESH_SECRET_KEY: str = "your-refresh-secret-key-here-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60  # 1 hour
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30  # 30 days

    # Admin
    ADMIN_SECRET_KEY: str = "change-this-admin-secret-key-in-production"  # Secret for admin registration

    # Google OAuth2
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/v1/auth/google/callback"

    # Bitcoin Payment Configuration
    BITCOIN_NETWORK: str = "testnet"  # "mainnet" or "testnet"
    BITCOIN_PERSONAL_WALLET: str = ""  # Your personal wallet address for fund forwarding
    BITCOIN_CONFIRMATIONS_REQUIRED: int = 3  # Number of confirmations required
    BITCOIN_PAYMENT_TIMEOUT_MINUTES: int = 60  # Payment timeout in minutes
    BITCOIN_API_URL: str = "https://blockstream.info/testnet/api"  # Blockchain API for testnet

    # Paystack Payment Configuration
    PAYSTACK_SECRET_KEY: str = ""  # Paystack secret key
    PAYSTACK_PUBLIC_KEY: str = ""  # Paystack public key
    PAYSTACK_WEBHOOK_SECRET: str = ""  # Paystack webhook secret for verification
    PAYSTACK_CURRENCY: str = "NGN"  # Currency code (NGN for Nigeria)
    PAYSTACK_API_URL: str = "https://api.paystack.co"  # Paystack API base URL

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
