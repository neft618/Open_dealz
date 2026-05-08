from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.notification import Notification
from app.models.user import User
from app.schemas.notification import NotificationResponse
from aiosmtplib import send
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings
from typing import List

async def notify(db: AsyncSession, user_id: str, type_: str, title: str, message: str, related_entity_type: str = None, related_entity_id: str = None):
    notification = Notification(
        user_id=user_id,
        type=type_,
        title=title,
        message=message,
        related_entity_type=related_entity_type,
        related_entity_id=related_entity_id
    )
    db.add(notification)
    await db.commit()

async def send_email(to_email: str, subject: str, body_html: str):
    msg = MIMEMultipart()
    msg['From'] = settings.smtp_username or "noreply@opendealz.com"
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body_html, 'html'))

    await send(
        msg,
        hostname=settings.smtp_host,
        port=settings.smtp_port,
        username=settings.smtp_username,
        password=settings.smtp_password,
        use_tls=True
    )

# Trigger points as in plan