"""Extension module for the Flask application"""

from pathlib import Path

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from celery import Celery

# Use absolute path for migrations directory (points to <repo>/src/migrations)
MIGRATION_DIR = str(Path(__file__).resolve().parents[1] / "migrations")

db = SQLAlchemy()
migrate = Migrate(directory=MIGRATION_DIR)

celery = Celery()

def init_celery(app):

    celery.conf.update(
        broker_url=app.config["CELERY_BROKER_URL"],
        result_backend=app.config["CELERY_RESULT_BACKEND"],
    )

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
