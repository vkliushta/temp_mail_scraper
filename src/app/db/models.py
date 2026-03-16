"""Database models"""

from sqlalchemy import Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.app.extensions import db


class EmailAddress(db.Model):
    __tablename__ = 'email_addresses'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    time_created: Mapped[DateTime] = mapped_column(DateTime, nullable=False)


class Email(db.Model):
    __tablename__ = 'emails'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    sender: Mapped[str] = mapped_column(String(255), nullable=False)
    email_id: Mapped[int] = mapped_column(ForeignKey('email_addresses.id'), nullable=False)
    time_received: Mapped[DateTime] = mapped_column(DateTime, nullable=False)

    recipient: Mapped['EmailAddress'] = relationship('EmailAddress', foreign_keys=[email_id])
