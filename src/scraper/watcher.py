"""Scheduler for managing background tasks related to email scraping"""

import asyncio
import datetime

from sqlalchemy import select

from src.app.settings import Config
from src.app.extensions import db
from src.app.db.models import EmailAddress, Email

from src.scraper.client import TempMailClient

client = TempMailClient()


async def watch():

    page = await client.open_page()

    processed = set()

    while True:
        try:

            # check if inbox still open
            if not page.url.startswith(Config.TEMP_MAIL_URL):
                await page.goto(Config.TEMP_MAIL_URL)

            address = await page.locator("#eposta_adres").get_attribute("value")

            # check if waiting for emails
            waiting = await page.locator(".eposta-bekleniyor").count()
            if waiting:
                await asyncio.sleep(10)
                continue

            rows = await page.locator(".mailler li.mail").all()

            for row in rows:

                row_id = await row.get_attribute("id")
                mail_id = row_id.replace("mail_", "")

                if mail_id in processed:
                    continue

                processed.add(mail_id)

                sender = await row.locator(".gonderen").inner_text()
                subject = await row.locator(".baslik").inner_text()

                link = await row.locator("a").get_attribute("href")

                # open email
                await page.goto(link)

                await page.wait_for_selector('div[dir="ltr"]', timeout=10000)

                body = await page.locator('div[dir="ltr"]').first.inner_text()

                await page.goto(Config.TEMP_MAIL_URL)

                email_address = db.session.execute(
                    select(EmailAddress).filter_by(email=address)
                ).scalars().one_or_none()

                if not email_address:
                    email_address = EmailAddress(email=address, time_created=datetime.datetime.now(datetime.timezone.utc))
                    db.session.add(email_address)
                    db.session.commit()

                exists = db.session.execute(
                    select(Email).filter_by(
                        sender=sender,
                        subject=subject,
                        recipient_id=email_address.id
                    )
                ).scalars().one_or_none()
                if exists:
                    continue

                email = Email(
                    sender=sender,
                    subject=subject,
                    body=body,
                    recipient_id=email_address.id,
                    time_received=datetime.datetime.now(datetime.timezone.utc),
                )

                db.session.add(email)
                db.session.commit()

            await asyncio.sleep(10)

        except Exception as e:
            print("Watcher error:", e)
            await asyncio.sleep(10)
