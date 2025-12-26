import os
import asyncio
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from concurrent.futures import ThreadPoolExecutor

load_dotenv()

# SMTP конфигурация из переменных окружения (под ваши названия)
SMTP_SERVER = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))  # 465 для SSL
SMTP_USERNAME = os.getenv("MAIL_FROM")  # Берём из MAIL_FROM
SMTP_PASSWORD = os.getenv("MAIL_PASSWORD")
SMTP_FROM_EMAIL = os.getenv("MAIL_FROM")  # Отправитель из MAIL_FROM


def send_otp_email_sync(email: str, otp_code: str) -> bool:
    """
    Send OTP code to user's email using SMTP (synchronous version)
    Returns True if sent successfully, False otherwise
    """
    # Проверка конфигурации
    if not all([SMTP_SERVER, SMTP_USERNAME, SMTP_PASSWORD]):
        print("SMTP configuration is incomplete. Please check environment variables.")
        print(f"SMTP_SERVER: {'Set' if SMTP_SERVER else 'Missing'}")
        print(f"SMTP_USERNAME (MAIL_FROM): {'Set' if SMTP_USERNAME else 'Missing'}")
        print(f"SMTP_PASSWORD: {'Set' if SMTP_PASSWORD else 'Missing'}")
        return False

    # Создаем сообщение
    message = MIMEMultipart("alternative")
    message["Subject"] = "Код подтверждения Workbench Flow"
    message["From"] = SMTP_FROM_EMAIL
    message["To"] = email

    # HTML версия письма
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Код подтверждения</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
            }}
            .container {{
                background-color: #f9f9f9;
                border-radius: 10px;
                padding: 30px;
                border: 1px solid #e0e0e0;
            }}
            .header {{
                text-align: center;
                margin-bottom: 30px;
            }}
            .otp-code {{
                background-color: #f0f0f0;
                border: 2px dashed #ccc;
                padding: 20px;
                text-align: center;
                font-size: 32px;
                font-weight: bold;
                letter-spacing: 6px;
                margin: 20px 0;
                border-radius: 5px;
                font-family: monospace;
            }}
            .footer {{
                margin-top: 30px;
                padding-top: 20px;
                border-top: 1px solid #eee;
                font-size: 12px;
                color: #666;
            }}
            .warning {{
                color: #d9534f;
                font-weight: bold;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h2>Код подтверждения</h2>
            </div>

            <p>Вы запросили код подтверждения для регистрации в сервисе <b>Workbench Flow</b>.</p>

            <p>Ваш код подтверждения:</p>
            <div class="otp-code">{otp_code}</div>

            <p>Код действителен в течение <span class="warning">2 минут</span>.</p>

            <p>Если вы не запрашивали этот код, просто проигнорируйте это письмо.</p>

            <div class="footer">
                <hr>
                <small>
                    С уважением,<br>
                    команда Workbench Flow
                </small>
            </div>
        </div>
    </body>
    </html>
    """

    # Текстовая версия для клиентов, не поддерживающих HTML
    text_content = f"""
Код подтверждения Workbench Flow

Вы запросили код подтверждения для регистрации в сервисе Workbench Flow.

Ваш код: {otp_code}

Код действителен в течение 2 минут.

Если вы не запрашивали этот код, просто проигнорируйте это письмо.

---
С уважением,
команда Workbench Flow
"""

    # Добавляем обе версии в письмо
    message.attach(MIMEText(text_content, "plain"))
    message.attach(MIMEText(html_content, "html"))

    try:
        # Настройка SSL контекста для безопасности
        context = ssl.create_default_context()

        # Для mail.ru на порту 465 используем SMTP_SSL
        if SMTP_PORT == 465:
            # Используем SSL соединение (подходит для mail.ru)
            with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, context=context) as server:
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                server.send_message(message)
                print(f"OTP email sent successfully to {email}")
                return True
        elif SMTP_PORT == 587:
            # Используем TLS соединение (STARTTLS)
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls(context=context)
                server.login(SMTP_USERNAME, SMTP_PASSWORD)
                server.send_message(message)
                print(f"OTP email sent successfully to {email}")
                return True
        else:
            # Для других портов без шифрования (не рекомендуется для продакшена)
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                if SMTP_USERNAME and SMTP_PASSWORD:
                    server.login(SMTP_USERNAME, SMTP_PASSWORD)
                server.send_message(message)
                print(f"OTP email sent successfully to {email}")
                return True

    except smtplib.SMTPAuthenticationError as e:
        print(f"SMTP authentication failed: {e}")
        print("Проверьте правильность MAIL_FROM и MAIL_PASSWORD")
        return False
    except smtplib.SMTPException as e:
        print(f"SMTP error occurred: {e}")
        return False
    except Exception as e:
        print(f"Failed to send email via SMTP: {e}")
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