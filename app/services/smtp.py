import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from app.config import settings as global_settings

from fastapi.templating import Jinja2Templates

from pydantic import EmailStr

from app.utils.logging import AppLogger
from app.utils.singleton import SingletonMetaNoArgs


logger = AppLogger().get_logger()


class SMTPEmailService(metaclass=SingletonMetaNoArgs):
    def __init__(self):
        self.server = smtplib.SMTP(
            global_settings.smtp.server, global_settings.smtp.port
        )
        self.server.starttls()
        self.server.login(global_settings.smtp.username, global_settings.smtp.password)
        self.templates = Jinja2Templates("templates")

    def send_email(
        self,
        sender: EmailStr,
        recipients: list[EmailStr],
        subject: str,
        body_text: str = "",
        body_html=None,
    ):
        msg = MIMEMultipart()
        msg["From"] = sender
        msg["To"] = ",".join(recipients)
        msg["Subject"] = subject
        msg.attach(MIMEText(body_text, "plain"))
        if body_html:
            msg.attach(MIMEText(body_html, "html"))
        self.server.sendmail(sender, recipients, msg.as_string())

    def send_template_email(
        self,
        recipients: list[EmailStr],
        subject: str,
        template: str = None,
        context: dict = None,
        sender: EmailStr = global_settings.smtp.from_email,
    ):
        template_str = self.templates.get_template(template)
        body_html = template_str.render(context)
        self.send_email(sender, recipients, subject, body_html=body_html)
