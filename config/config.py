import os


class Config:
    """Configuración de la aplicación"""

    # Database
    DATABASE_PATH = os.getenv("DB_PATH", "notifications.db")

    # Templates
    TEMPLATES_PATH = os.getenv("TEMPLATES_PATH", "templates")

    # SMTP Configuration
    SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", "")

    # Twilio Configuration
    TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_FROM_PHONE = os.getenv("TWILIO_FROM_PHONE", "")

    # WhatsApp Configuration
    WHATSAPP_API_TOKEN = os.getenv("WHATSAPP_API_TOKEN", "")
    WHATSAPP_PHONE_ID = os.getenv("WHATSAPP_PHONE_ID", "")
