"""Configuration management for Retail Analytics Dashboard.

This module provides centralized configuration management using environment variables
with sensible defaults for different deployment environments.
"""

import os
from typing import Optional
from dataclasses import dataclass
from pathlib import Path


class ConfigurationError(Exception):
    """Raised when configuration is invalid or missing required values."""
    pass


@dataclass
class DatabaseConfig:
    """Database configuration settings."""
    host: str
    port: int
    name: str
    user: str
    password: str
    pool_size: int = 5
    max_overflow: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 3600
    
    @property
    def url(self) -> str:
        """Generate SQLAlchemy database URL."""
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"


@dataclass
class RedisConfig:
    """Redis cache configuration settings."""
    host: str
    port: int
    db: int = 0
    password: Optional[str] = None
    socket_timeout: int = 5
    socket_connect_timeout: int = 5
    
    @property
    def url(self) -> str:
        """Generate Redis connection URL."""
        if self.password:
            return f"redis://:{self.password}@{self.host}:{self.port}/{self.db}"
        return f"redis://{self.host}:{self.port}/{self.db}"


class Config:
    """Base configuration class with common settings."""
    
    # Application settings
    APP_NAME = "Retail Analytics Dashboard"
    DEBUG = False
    TESTING = False
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    
    # Flask settings
    JSON_SORT_KEYS = False
    JSONIFY_PRETTYPRINT_REGULAR = True
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file upload
    
    # Database settings
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 3600,
    }
    
    # Logging settings
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE = os.getenv("LOG_FILE", "logs/app.log")
    
    # Security settings
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", SECRET_KEY)
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", "3600"))  # 1 hour
    JWT_REFRESH_TOKEN_EXPIRES = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES", "2592000"))  # 30 days
    
    # CORS settings
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")
    
    # Rate limiting
    RATELIMIT_ENABLED = os.getenv("RATELIMIT_ENABLED", "true").lower() == "true"
    RATELIMIT_DEFAULT = os.getenv("RATELIMIT_DEFAULT", "100 per hour")
    RATELIMIT_STORAGE_URL = None  # Will be set from Redis config
    
    # Cache settings
    CACHE_TYPE = os.getenv("CACHE_TYPE", "redis")
    CACHE_DEFAULT_TIMEOUT = int(os.getenv("CACHE_DEFAULT_TIMEOUT", "300"))  # 5 minutes
    
    # Data directory
    DATA_DIR = Path(os.getenv("DATA_DIR", "data"))
    
    @staticmethod
    def get_database_config() -> DatabaseConfig:
        """Get database configuration from environment variables.
        
        Returns:
            DatabaseConfig: Database configuration object.
            
        Raises:
            ConfigurationError: If required database variables are missing.
        """
        required_vars = ["DB_HOST", "DB_NAME", "DB_USER", "DB_PASSWORD"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            raise ConfigurationError(
                f"Missing required database environment variables: {', '.join(missing_vars)}"
            )
        
        return DatabaseConfig(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT", "5432")),
            name=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            pool_size=int(os.getenv("DB_POOL_SIZE", "5")),
            max_overflow=int(os.getenv("DB_MAX_OVERFLOW", "10")),
            pool_timeout=int(os.getenv("DB_POOL_TIMEOUT", "30")),
            pool_recycle=int(os.getenv("DB_POOL_RECYCLE", "3600")),
        )
    
    @staticmethod
    def get_redis_config() -> RedisConfig:
        """Get Redis configuration from environment variables.
        
        Returns:
            RedisConfig: Redis configuration object.
        """
        return RedisConfig(
            host=os.getenv("REDIS_HOST", "localhost"),
            port=int(os.getenv("REDIS_PORT", "6379")),
            db=int(os.getenv("REDIS_DB", "0")),
            password=os.getenv("REDIS_PASSWORD"),
            socket_timeout=int(os.getenv("REDIS_SOCKET_TIMEOUT", "5")),
            socket_connect_timeout=int(os.getenv("REDIS_CONNECT_TIMEOUT", "5")),
        )
    
    @classmethod
    def validate(cls) -> None:
        """Validate configuration settings.
        
        Raises:
            ConfigurationError: If configuration is invalid.
        """
        # Validate secret key in production
        if not cls.DEBUG and cls.SECRET_KEY == "dev-secret-key-change-in-production":
            raise ConfigurationError(
                "SECRET_KEY must be set to a secure random value in production"
            )
        
        # Create required directories
        log_dir = Path(cls.LOG_FILE).parent
        log_dir.mkdir(parents=True, exist_ok=True)
        cls.DATA_DIR.mkdir(parents=True, exist_ok=True)


class DevelopmentConfig(Config):
    """Development environment configuration."""
    DEBUG = True
    TESTING = False
    LOG_LEVEL = "DEBUG"
    
    # Use SQLite for local development if PostgreSQL not available
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///retail_analytics_dev.db"
    )


class TestingConfig(Config):
    """Testing environment configuration."""
    DEBUG = True
    TESTING = True
    LOG_LEVEL = "DEBUG"
    
    # Use in-memory SQLite for tests
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    
    # Disable CSRF for testing
    WTF_CSRF_ENABLED = False
    
    # Disable rate limiting in tests
    RATELIMIT_ENABLED = False


class ProductionConfig(Config):
    """Production environment configuration."""
    DEBUG = False
    TESTING = False
    LOG_LEVEL = os.getenv("LOG_LEVEL", "WARNING")
    
    @classmethod
    def init_app(cls) -> None:
        """Initialize production-specific settings."""
        Config.validate()
        
        # Get database configuration
        db_config = cls.get_database_config()
        cls.SQLALCHEMY_DATABASE_URI = db_config.url
        cls.SQLALCHEMY_ENGINE_OPTIONS.update({
            "pool_size": db_config.pool_size,
            "max_overflow": db_config.max_overflow,
            "pool_timeout": db_config.pool_timeout,
            "pool_recycle": db_config.pool_recycle,
        })
        
        # Get Redis configuration
        redis_config = cls.get_redis_config()
        cls.CACHE_REDIS_URL = redis_config.url
        cls.RATELIMIT_STORAGE_URL = redis_config.url


# Configuration mapping
config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}


def get_config(env_name: Optional[str] = None) -> Config:
    """Get configuration object based on environment name.
    
    Args:
        env_name: Environment name (development, testing, production).
                 If None, uses FLASK_ENV environment variable.
    
    Returns:
        Config: Configuration object for the specified environment.
    """
    if env_name is None:
        env_name = os.getenv("FLASK_ENV", "development")
    
    config_class = config_by_name.get(env_name.lower(), DevelopmentConfig)
    
    # Initialize production config if needed
    if env_name.lower() == "production":
        config_class.init_app()
    
    return config_class
