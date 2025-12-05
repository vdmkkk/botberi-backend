from fastapi import BackgroundTasks

from app.core.config import get_settings

settings = get_settings()


def _render_verification_email(code: str) -> str:
    return f"""
    <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>Welcome to Botberi 👋</h2>
            <p>Your verification code:</p>
            <p style="font-size: 32px; letter-spacing: 6px; font-weight: bold;">{code}</p>
            <p>This code expires in {settings.registration_code_ttl_seconds // 60} minutes.</p>
        </body>
    </html>
    """


def _render_reset_email(link: str) -> str:
    return f"""
    <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>Password reset requested</h2>
            <p>Click the link below to pick a new password. It expires in {settings.password_reset_ttl_seconds // 60} minutes.</p>
            <p><a href="{link}" style="color:#6C63FF;font-weight:bold;">Reset Password</a></p>
        </body>
    </html>
    """


def queue_verification_email(background_tasks: BackgroundTasks, email: str, code: str) -> None:
    subject = settings.verification_email_subject
    html = _render_verification_email(code)
    background_tasks.add_task(_log_email, email, subject, html)


def queue_password_reset_email(background_tasks: BackgroundTasks, email: str, link: str) -> None:
    subject = settings.password_reset_email_subject
    html = _render_reset_email(link)
    background_tasks.add_task(_log_email, email, subject, html)


def _log_email(recipient: str, subject: str, html_content: str) -> None:
    # Placeholder for a real transactional email service. Logged for observability in dev.
    print(f"[EMAIL] to={recipient} subject={subject}\n{html_content}")


__all__ = ["queue_verification_email", "queue_password_reset_email"]


