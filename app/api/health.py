from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request, status
from pydantic import EmailStr
from rotoger import get_logger
from starlette.concurrency import run_in_threadpool

from app.services.smtp import SMTPEmailService

logger = get_logger()

router = APIRouter()




@router.get("/redis", status_code=status.HTTP_200_OK)
async def redis_check(request: Request):
    """
    Endpoint to check Redis health and retrieve server information.

    This endpoint connects to the Redis client configured in the application
    and attempts to fetch server information using the `info()` method.
    If an error occurs during the Redis operation, it logs the error.

    Args:
        request (Request): The incoming HTTP request.

    Returns:
        dict or None: Returns Redis server information as a dictionary if successful,
        otherwise returns `None` in case of an error.
    """
    redis_client = await request.app.redis
    redis_info = None
    try:
        redis_info = await redis_client.info()
    except Exception as e:
        await logger.aerror(f"Redis error: {e}")
    return redis_info


@router.post("/email", status_code=status.HTTP_200_OK)
async def smtp_check(
    request: Request,
    smtp: Annotated[SMTPEmailService, Depends()],
    sender: Annotated[EmailStr, Query(description="Email address of the sender")],
    recipients: Annotated[
        list[EmailStr], Query(description="List of recipient email addresses")
    ],
    subject: Annotated[str, Query(description="Subject line of the email")],
    body_text: Annotated[str, Query(description="Body text of the email")] = "",
):
    """
    Endpoint to send an email via an SMTP service.

    This endpoint facilitates sending an email using the configured SMTP service. It performs
    the operation in a separate thread using `run_in_threadpool`, which is suitable for blocking I/O
    operations, such as sending emails. By offloading the sending process to a thread pool, it prevents
    the asynchronous event loop from being blocked, ensuring that other tasks in the application
    remain responsive.

    Args:
        request (Request): The incoming HTTP request, providing context such as the base URL.
        smtp (SMTPEmailService): The SMTP email service dependency injected to send emails.
        sender (EmailStr): The sender's email address.
        recipients (list[EmailStr]): A list of recipient email addresses.
        subject (str): The subject line of the email.
        body_text (str, optional): The plain-text body of the email. Defaults to an empty string.

    Returns:
        dict: A JSON object indicating success with a message, e.g., {"message": "Email sent"}.

    Logs:
        Logs relevant email metadata: request base URL, sender, recipients, and subject.

    Why `run_in_threadpool`:
        Sending an email often involves interacting with external SMTP servers, which can be
        a slow, blocking operation. Using `run_in_threadpool` is beneficial because:
        1. Blocking I/O operations like SMTP requests do not interrupt the main event loop,
           preventing other tasks (e.g., handling HTTP requests) from slowing down.
        2. The email-sending logic is offloaded to a separate, managed thread pool, improving
           application performance and scalability.
    """

    email_data = {
        "base_url": request.base_url,
        "sender": sender,
        "recipients": recipients,
        "subject": subject,
    }

    await logger.ainfo("Sending email.", email_data=email_data)

    await run_in_threadpool(
        smtp.send_email,
        sender=sender,
        recipients=recipients,
        subject=subject,
        body_text=body_text,
        body_html=None,
    )
    return {"message": "Email sent"}
