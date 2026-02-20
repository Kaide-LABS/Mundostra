"""GmailSender — sends HTML emails via Gmail SMTP with App Password."""

from __future__ import annotations

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import aiosmtplib

from backend.logging_config import get_logger

logger = get_logger(__name__)


class GmailSender:
    """Sends HTML emails via Gmail SMTP using an App Password.

    Uses aiosmtplib for async SMTP. Fire-and-forget pattern (no replies tracked).
    """

    def __init__(
        self,
        sender_email: str,
        app_password: str,
        recipient_email: str,
    ) -> None:
        self.sender_email = sender_email
        self.app_password = app_password
        self.recipient_email = recipient_email

    async def send_resolution(
        self,
        *,
        event_id: str,
        email: dict[str, str],
    ) -> bool:
        """Send an HTML email.

        Args:
            event_id: For logging.
            email: Dict with 'subject' and 'html_body' keys.

        Returns True on success, False otherwise.
        """
        try:
            msg = MIMEMultipart("alternative")
            msg["From"] = self.sender_email
            msg["To"] = self.recipient_email
            msg["Subject"] = email["subject"]
            msg.attach(MIMEText(email["html_body"], "html"))

            await aiosmtplib.send(
                msg,
                hostname="smtp.gmail.com",
                port=587,
                start_tls=True,
                username=self.sender_email,
                password=self.app_password,
            )

            await logger.ainfo(
                "email_sent",
                event_id=event_id,
                success=True,
                recipient=self.recipient_email,
            )
            return True

        except Exception as exc:
            await logger.aerror(
                "email_send_failed",
                event_id=event_id,
                error=str(exc),
            )
            return False
