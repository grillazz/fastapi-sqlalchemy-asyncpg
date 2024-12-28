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
    """
    SMTPEmailService provides a reusable interface to send emails via an SMTP server.

    This service supports plaintext and HTML emails, and also allows
    sending template-based emails using the Jinja2 template engine.

    It is implemented as a singleton to ensure that only one SMTP connection is maintained
    throughout the application lifecycle, optimizing resource usage.

    Attributes:
        server_host (str): SMTP server hostname or IP address.
        server_port (int): Port number for the SMTP connection.
        username (str): SMTP username for authentication.
        password (str): SMTP password for authentication.
        templates (Jinja2Templates): Jinja2Templates instance for loading and rendering email templates.
        server (smtplib.SMTP): An SMTP object for sending emails, initialized after object creation.
    """

    # SMTP configuration
    server_host: str = field(default=global_settings.smtp.server)
    server_port: int = field(default=global_settings.smtp.port)
    username: str = field(default=global_settings.smtp.username)
    password: str = field(default=global_settings.smtp.password)

    # Dependencies
    templates: Jinja2Templates = field(
        factory=lambda: Jinja2Templates(global_settings.smtp.template_path)
    )
    server: smtplib.SMTP = field(init=False)  # Deferred initialization in post-init

    def __attrs_post_init__(self):
        """
        Initializes the SMTP server connection after the object is created.

        This method sets up a secure connection to the SMTP server, including STARTTLS encryption
        and logs in using the provided credentials.
        """
        self.server = smtplib.SMTP(self.server_host, self.server_port)
        self.server.starttls() # Upgrade the connection to secure TLS
        self.server.login(self.username, self.password)
        logger.info("SMTPEmailService initialized successfully and connected to SMTP server.")

    def _prepare_email(
        self,
        sender: EmailStr,
        recipients: list[EmailStr],
        subject: str,
        body_text: str,
        body_html: str,
    ) -> MIMEMultipart:
        """
        Prepares a MIME email message with the given plaintext and HTML content.

        Args:
            sender (EmailStr): The email address of the sender.
            recipients (list[EmailStr]): A list of recipient email addresses.
            subject (str): The subject line of the email.
            body_text (str): The plaintext content of the email.
            body_html (str): The HTML content of the email (optional).

        Returns:
            MIMEMultipart: A MIME email object ready to be sent.
        """
        msg = MIMEMultipart()
        msg["From"] = sender
        msg["To"] = ",".join(recipients)
        msg["Subject"] = subject
        # Add plain text and HTML content (if provided)
        msg.attach(MIMEText(body_text, "plain"))
        if body_html:
            msg.attach(MIMEText(body_html, "html"))
        logger.debug(f"Prepared email from {sender} to {recipients}.")
        return msg

    def send_email(
        self,
        sender: EmailStr,
        recipients: list[EmailStr],
        subject: str,
        body_text: str = "",
        body_html: str = None,
    ):
        """
        Sends an email to the specified recipients.

        Supports plaintext and HTML email content. This method constructs
        the email message using `_prepare_email` and sends it using the SMTP server.

        Args:
            sender (EmailStr): The email address of the sender.
            recipients (list[EmailStr]): A list of recipient email addresses.
            subject (str): The subject line of the email.
            body_text (str): The plaintext content of the email.
            body_html (str): The HTML content of the email (optional).

        Raises:
            smtplib.SMTPException: If the email cannot be sent.
        """
        try:
            msg = self._prepare_email(sender, recipients, subject, body_text, body_html)
            self.server.sendmail(sender, recipients, msg.as_string())
            logger.info(f"Email sent successfully to {recipients} from {sender}.")
        except smtplib.SMTPException as e:
            logger.error("Failed to send email", exc_info=e)
            raise

    def send_template_email(
        self,
        recipients: list[EmailStr],
        subject: str,
        template: str,
        context: dict,
        sender: EmailStr,
    ):
        """
        Sends an email using a Jinja2 template.

        This method renders the template with the provided context and sends it
        to the specified recipients.

        Args:
            recipients (list[EmailStr]): A list of recipient email addresses.
            subject (str): The subject line of the email.
            template (str): The name of the template file in the templates directory.
            context (dict): A dictionary of values to render the template with.
            sender (EmailStr): The email address of the sender.

        Raises:
            jinja2.TemplateNotFound: If the specified template is not found.
            smtplib.SMTPException: If the email cannot be sent.
        """
        try:
            template_str = self.templates.get_template(template)
            body_html = template_str.render(context)  # Render the HTML using context variables
            self.send_email(sender, recipients, subject, body_html=body_html)
            logger.info(f"Template email sent successfully to {recipients} using template {template}.")
        except Exception as e:
            logger.error("Failed to send template email", exc_info=e)
            raise