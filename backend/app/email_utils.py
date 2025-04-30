import secrets
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from pydantic import EmailStr
from . import config

# Email configuration
email_config = ConnectionConfig(
    MAIL_USERNAME=config.MAIL_USERNAME,
    MAIL_PASSWORD=config.MAIL_PASSWORD,
    MAIL_FROM=config.MAIL_FROM,
    MAIL_PORT=config.MAIL_PORT,
    MAIL_SERVER=config.MAIL_SERVER,
    MAIL_FROM_NAME=config.MAIL_FROM_NAME,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

async def send_verification_email(email: EmailStr, verification_code: str):
    """
    Send verification email to the user
    """
    # Configure email contents
    verification_url = f"{config.VERIFICATION_URL_BASE}/verify-email?code={verification_code}&email={email}"
    
    message = MessageSchema(
        subject="Plan Tracker - Email Verification",
        recipients=[email],
        body=f"""
        <html>
        <body>
            <h1>Welcome to Plan Tracker!</h1>
            <p>Thank you for signing up. Please verify your email address by clicking the link below:</p>
            <p><a href="{verification_url}">Verify Email Address</a></p>
            <p>Or enter this verification code: <strong>{verification_code}</strong></p>
            <p>If you did not sign up for Plan Tracker, please ignore this email.</p>
        </body>
        </html>
        """,
        subtype="html"
    )
    
    # Send email
    fm = FastMail(email_config)
    await fm.send_message(message)

def generate_verification_code():
    """
    Generate a verification code (6 alphanumeric characters)
    """
    return secrets.token_hex(3)  # 6 hex characters 