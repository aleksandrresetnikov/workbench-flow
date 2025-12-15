import os
import asyncio
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor
import resend

load_dotenv()

resend.api_key = os.getenv("RESEND_API_KEY")
RESEND_FROM = os.getenv("RESEND_FROM")


def send_otp_email_sync(email: str, otp_code: str) -> bool:
    """
    Send OTP code to user's email (synchronous version, Resend)
    Returns True if sent successfully, False otherwise
    """
    try:
        resend.Emails.send({
            "from": RESEND_FROM,
            "to": [email],
            "subject": "Код подтверждения Workbench Flow",
            "html": f"""
                        <h2>Код подтверждения</h2>
                        <p>Вы запросили код подтверждения для регистрации в сервисе <b>Workbench Flow</b>.</p>

                        <p>Ваш код:</p>
                        <h1 style="letter-spacing: 6px;">{otp_code}</h1>

                        <p>Код действителен в течение <b>2 минут</b>.</p>

                        <p>
                            Если вы не запрашивали этот код, просто проигнорируйте это письмо.
                        </p>

                        <hr />
                        <small>
                            С уважением,<br />
                            команда Workbench Flow
                        </small>
                    """
        })
        print(f"OTP email sent successfully to {email}")
        return True

    except Exception as e:
        print(f"Failed to send email via Resend: {e}")
        return False


async def send_otp_email(email: str, otp_code: str) -> bool:
    """
    Send OTP code to user's email (asynchronous version)
    """
    loop = asyncio.get_running_loop()
    with ThreadPoolExecutor(max_workers=1) as executor:
        return await loop.run_in_executor(
            executor,
            send_otp_email_sync,
            email,
            otp_code
        )
