"""Reusable Celery tasks for the scraper package."""

import asyncio
import datetime

from sqlalchemy import select

from src.app.extensions import celery, db
from src.app.db.models import EmailAddress
from src.scraper.client import TempMailClient
from src.scraper.watcher import watch

client = TempMailClient()


@celery.task
def refresh_email_task():
    """Refreshes/creates a temp email address and returns it."""
    email = asyncio.run(client.refresh_email())
    
    with celery.app.app_context():
        existing = db.session.execute(
            select(EmailAddress).filter_by(email=email)
        ).first()

        if not existing:
            existing = EmailAddress(email=email, time_created=datetime.datetime.now(datetime.timezone.utc))
            db.session.add(existing)
            db.session.commit()

        return email


@celery.task
def start_inbox_watcher():
    asyncio.run(watch())
