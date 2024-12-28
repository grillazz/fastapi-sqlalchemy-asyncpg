from attrs import define, field
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.config import settings as global_settings

from fastapi.templating import Jinja2Templates

from pydantic import EmailStr

from app.utils.logging import AppLogger
from app.utils.singleton import SingletonMetaNoArgs


logger = AppLogger().get_logger()


@define
class SMTPEmailService(metaclass=SingletonMetaNoArgs):
    # SMTP configuration
    server_host: str = field(default=global_settings.smtp.server)
    server_port: int = field(default=global_settings.smtp.port)
    username: str = field(default=global_settings.smtp.username)
    password: str = field(default=global_settings.smtp.password)

    # Dependencies
    templates: Jinja2Templates = field(
        factory=lambda: Jinja2Templates(global_settings.templates_dir)
    )
    server: smtplib.SMTP = field(init=False)  # Deferred initialization in post-init

    def __attrs_post_init__(self):
        """Initialize the SMTP server connection after object creation."""
        self.server = smtplib.SMTP(self.server_host, self.server_port)
        self.server.starttls()
        self.server.login(self.username, self.password)

    def _prepare_email(
        self,
        sender: EmailStr,
        recipients: list[EmailStr],
        subject: str,
        body_text: str,
        body_html: str,
    ) -> MIMEMultipart:
        """Prepare the email message."""
        msg = MIMEMultipart()
        msg["From"] = sender
        msg["To"] = ",".join(recipients)
        msg["Subject"] = subject
        msg.attach(MIMEText(body_text, "plain"))
        if body_html:
            msg.attach(MIMEText(body_html, "html"))
        return msg

    def send_email(
        self,
        sender: EmailStr,
        recipients: list[EmailStr],
        subject: str,
        body_text: str = "",
        body_html: str = None,
    ):
        """Send a regular email (plain text or HTML)."""
        msg = self._prepare_email(sender, recipients, subject, body_text, body_html)
        self.server.sendmail(sender, recipients, msg.as_string())

    def send_template_email(
        self,
        recipients: list[EmailStr],
        subject: str,
        template: str,
        context: dict,
        sender: EmailStr,
    ):
        """Send an email using a template with the provided context."""
        template_str = self.templates.get_template(template)
        body_html = template_str.render(context)
        self.send_email(sender, recipients, subject, body_html=body_html)
