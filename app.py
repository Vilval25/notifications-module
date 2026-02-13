"""
Punto de entrada principal de la aplicación REST API
Ejecutar con: python app.py
"""

from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

from config.config import Config
from src.interface.notification_controller import NotificationController
from src.business.notification_service import NotificationService
from src.business.handlebars_engine import HandlebarsEngine
from src.business.sender_factory import SenderFactory
from src.infrastructure.senders.smtp_sender import SmtpSender
from src.infrastructure.senders.twilio_sms_sender import TwilioSmsSender
from src.infrastructure.senders.meta_whatsapp_sender import MetaWhatsAppSender
from src.infrastructure.repository.sql_notification_repository import SqlNotificationRepository
from src.api import create_app


def initialize_controller() -> NotificationController:
    """
    Inicializa y configura todos los componentes de la aplicación

    Returns:
        NotificationController configurado y listo para usar
    """
    # Configurar repositorio
    repository = SqlNotificationRepository(Config.DATABASE_PATH)

    # Configurar motor de plantillas
    template_engine = HandlebarsEngine(Config.TEMPLATES_PATH)

    # Configurar senders
    smtp_sender = SmtpSender(
        host=Config.SMTP_HOST,
        port=Config.SMTP_PORT,
        username=Config.SMTP_USERNAME,
        password=Config.SMTP_PASSWORD,
        from_email=Config.SMTP_FROM_EMAIL
    )

    sms_sender = TwilioSmsSender(
        account_sid=Config.TWILIO_ACCOUNT_SID,
        auth_token=Config.TWILIO_AUTH_TOKEN,
        from_phone=Config.TWILIO_FROM_PHONE
    )

    whatsapp_sender = MetaWhatsAppSender(
        api_token=Config.WHATSAPP_API_TOKEN,
        phone_number_id=Config.WHATSAPP_PHONE_ID
    )

    # Configurar factory
    sender_factory = SenderFactory(smtp_sender, sms_sender, whatsapp_sender)

    # Configurar servicio
    notification_service = NotificationService(
        template_engine=template_engine,
        sender_factory=sender_factory,
        repository=repository
    )

    # Configurar controlador
    return NotificationController(notification_service)


if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Servidor de Notificaciones REST API")
    print("=" * 60)
    print("\nInicializando componentes...")

    # Inicializar controlador
    controller = initialize_controller()

    # Crear aplicación Flask
    app = create_app(controller)

    print("\nEndpoints disponibles:")
    print("  • GET  http://localhost:5000/")
    print("  • GET  http://localhost:5000/health")
    print("  • POST http://localhost:5000/api/notifications/send")
    print("  • GET  http://localhost:5000/api/notifications/logs")
    print("\n" + "=" * 60)
    print("Servidor iniciado en http://localhost:5000")
    print("Presiona Ctrl+C para detener")
    print("=" * 60 + "\n")

    # Ejecutar servidor
    app.run(debug=True, host='0.0.0.0', port=5000)
