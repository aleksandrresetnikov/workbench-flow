import smtplib
import os
import asyncio
import socket
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor

load_dotenv()
socket.setdefaulttimeout(10)

SMTP_FROM = os.getenv("SMTP_FROM")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))


def send_otp_email_sync(email: str, otp_code: str) -> bool:
    """
    Send OTP code to user's email (synchronous version)
    Returns True if sent successfully, False otherwise
    """
    try:
        msg = MIMEMultipart()
        msg["From"] = SMTP_FROM
        msg["To"] = email
        msg["Subject"] = "Your OTP Code for Workbench Flow Registration"

        body = f"""Hello!

Your OTP code for registration on Workbench Flow is:

{otp_code}

This code will expire in 2 minutes.

If you didn't request this code, please ignore this email.

Best regards,
Workbench Flow Team
"""
        msg.attach(MIMEText(body, "plain"))

        print("Connecting to SMTP...")
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as server:
            server.set_debuglevel(0)  # поставь 1, если нужно дебажить
            server.ehlo()
            server.starttls()
            server.ehlo()

            print("Logging in...")
            server.login(SMTP_FROM, SMTP_PASSWORD)

            print("Sending email...")
            server.sendmail(SMTP_FROM, email, msg.as_string())

        print(f"OTP email sent successfully to {email}")
        return True

    except smtplib.SMTPAuthenticationError as e:
        print(f"SMTP Authentication Error: {e}")
        return False
    except smtplib.SMTPConnectError as e:
        print(f"SMTP Connection Error: {e}")
        return False
    except smtplib.SMTPException as e:
        print(f"SMTP Error: {e}")
        return False
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False


async def send_otp_email(email: str, otp_code: str) -> bool:
    """
    Send OTP code to user's email (asynchronous version)
    Returns True if sent successfully, False otherwise
    """
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor(max_workers=1) as executor:
        return await loop.run_in_executor(
            executor,
            send_otp_email_sync,
            email,
            otp_code
        )
