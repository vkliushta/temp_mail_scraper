"""Settings module for the Flask application"""

import os


class Config:

    SQLALCHEMY_DATABASE_URI = (
        f"postgresql+psycopg2://"
        f"{os.getenv('POSTGRES_USER','postgres')}:"
        f"{os.getenv('POSTGRES_PASSWORD','postgres')}"
        f"@db/{os.getenv('POSTGRES_DB','app_db')}"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CELERY_BROKER_URL = os.getenv(
        "CELERY_BROKER_URL", "redis://redis:6379/0"
    )
    CELERY_RESULT_BACKEND = os.getenv(
        "CELERY_RESULT_BACKEND", "redis://redis:6379/0"
    )

    TEMP_MAIL_URL = "https://tempail.com/ua/"


class TestConfig:
    """Test config used for testing purposes"""
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    TESTING = True
