"""Flask app module"""

from flask_migrate import upgrade
import os
from flask import Flask

from src.app.extensions import db, migrate, init_celery


def create_app():
    app = Flask(__name__)

    app.config.from_object('src.app.settings.Config')

    db.init_app(app)
    migrate.init_app(app, db)

    from src.app.api.email_blueprint import blueprint as email_blueprint
    app.register_blueprint(email_blueprint)

    # Run migrations only in the Flask app container (not in Celery workers)
    is_celery = os.getenv('IS_CELERY', 'false').lower() == 'true'
    if not is_celery:
        with app.app_context():
            upgrade()

    init_celery(app)

    from src.app.db.models import Email, EmailAddress

    if not is_celery:
        from src.scraper.tasks import start_inbox_watcher
        with app.app_context():
            start_inbox_watcher.delay()

    return app
