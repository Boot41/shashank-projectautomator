import smtplib
from email.message import EmailMessage
from typing import Optional

from ..config.settings import settings


async def send_email(to_email: str, subject: str, body: str) -> dict:
    if not (settings.smtp_host and settings.smtp_port and settings.smtp_user and settings.smtp_password and settings.smtp_from_email):
        return {"status": "error", "error": "SMTP not configured. Please set SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, and SMTP_FROM_EMAIL in your .env file"}

    msg = EmailMessage()
    msg["From"] = settings.smtp_from_email if not settings.smtp_from_name else f"{settings.smtp_from_name} <{settings.smtp_from_email}>"
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    try:
        with smtplib.SMTP(settings.smtp_host, int(settings.smtp_port)) as server:
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_password)
            server.send_message(msg)
        return {"status": "sent"}
    except Exception as e:
        return {"status": "error", "error": str(e)}


