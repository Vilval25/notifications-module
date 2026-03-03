"""
Punto de entrada principal de la aplicación REST API con FastAPI
Ejecutar con: python app.py
"""

from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

import uvicorn
from config.config import Config
from src.interface.notification_controller import NotificationController
from src.business.notification_service import NotificationService
from src.business.handlebars_engine import HandlebarsEngine
from src.business.sender_factory import SenderFactory
from src.business.template_service import TemplateService
from src.infrastructure.senders.smtp_sender import SmtpSender
from src.infrastructure.senders.mock_sms_sender import MockSmsSender
from src.infrastructure.senders.mock_whatsapp_sender import MockWhatsAppSender
from src.infrastructure.repository.sql_notification_log_repository import SqlNotificationLogRepository
from src.infrastructure.repository.sql_template_event_repository import TemplateEventRepository
from src.infrastructure.repository.sql_internal_notification_repository import InternalNotificationRepository
from src.business.internal_notification_service import InternalNotificationService
from src.infrastructure.repository.sql_subscription_repository import SubscriptionRepository
from src.business.subscription_service import SubscriptionService
from src.business.event_notification_service import EventNotificationService
from src.api import create_app
from src.api.internal_notification_routes import register_internal_notification_routes
from src.api.subscription_routes import register_subscription_routes
from src.api.event_notification_routes import register_event_notification_routes


def initialize_controller() -> tuple[NotificationController, TemplateService, TemplateEventRepository, InternalNotificationService, SubscriptionService, EventNotificationService]:
    """
    Inicializa y configura todos los componentes de la aplicación

    Returns:
        Tupla con NotificationController, TemplateService, TemplateEventRepository, InternalNotificationService, SubscriptionService y EventNotificationService configurados
    """
    # Configurar repositorio de logs de notificaciones
    repository = SqlNotificationLogRepository(Config.DATABASE_PATH)

    # Configurar repositorio de eventos de plantillas
    event_repository = TemplateEventRepository(Config.DATABASE_PATH)

    # Configurar repositorio de notificaciones internas
    internal_notification_repository = InternalNotificationRepository(Config.DATABASE_PATH)

    # Configurar servicio de notificaciones internas
    internal_notification_service = InternalNotificationService(internal_notification_repository)

    # Configurar repositorio de suscripciones
    subscription_repository = SubscriptionRepository(Config.DATABASE_PATH)

    # Configurar servicio de suscripciones
    subscription_service = SubscriptionService(subscription_repository)

    # Configurar motor de plantillas
    template_engine = HandlebarsEngine(Config.TEMPLATES_PATH)

    # Configurar servicio de templates (con event_repository)
    template_service = TemplateService(Config.TEMPLATES_PATH, event_repository)

    # Configurar senders
    smtp_sender = SmtpSender(
        host=Config.SMTP_HOST,
        port=Config.SMTP_PORT,
        username=Config.SMTP_USERNAME,
        password=Config.SMTP_PASSWORD,
        from_email=Config.SMTP_FROM_EMAIL
    )

    # Configurar senders mock (simulan envío sin servicios externos)
    sms_sender = MockSmsSender()
    whatsapp_sender = MockWhatsAppSender()

    # Configurar factory
    sender_factory = SenderFactory(smtp_sender, sms_sender, whatsapp_sender)

    # Configurar servicio
    notification_service = NotificationService(
        template_engine=template_engine,
        sender_factory=sender_factory,
        repository=repository
    )

    # Configurar controlador
    controller = NotificationController(notification_service)

    # Configurar servicio orquestador de eventos
    event_notification_service = EventNotificationService(
        internal_notification_service=internal_notification_service,
        subscription_service=subscription_service,
        notification_controller=controller
    )

    return controller, template_service, event_repository, internal_notification_service, subscription_service, event_notification_service


if __name__ == '__main__':
    print("=" * 60)
    print("Servidor de Notificaciones REST API con FastAPI")
    print("=" * 60)
    print("\nInicializando componentes...")

    # Inicializar componentes
    controller, template_service, event_repository, internal_notification_service, subscription_service, event_notification_service = initialize_controller()

    # Crear aplicación FastAPI
    app = create_app(controller, template_service, event_repository)

    # Registrar rutas de notificaciones internas
    register_internal_notification_routes(app, internal_notification_service)

    # Registrar rutas de suscripciones
    register_subscription_routes(app, subscription_service)

    # Registrar rutas de eventos unificados
    register_event_notification_routes(app, event_notification_service)

    print("\nComponentes inicializados correctamente")
    print("\n" + "=" * 60)
    print("ENDPOINTS PRINCIPALES PARA MÓDULOS EXTERNOS")
    print("=" * 60)
    print("\nEndpoints para Modulos Externos:")
    print("  - POST http://localhost:8000/api/events/tramite")
    print("  - POST http://localhost:8000/api/events/creacion-cuenta")
    print("  - POST http://localhost:8000/api/events/cambio-contrasena")
    print("\n" + "=" * 60)
    print("\nOtros Endpoints:")
    print("  - GET  http://localhost:8000/")
    print("  - GET  http://localhost:8000/health")
    print("  - GET  http://localhost:8000/api/notifications/logs")
    print("\nGestion de Plantillas:")
    print("  - UI:         http://localhost:8000/templates-ui")
    print("  - API:        http://localhost:8000/api/templates")
    print("\nNotificaciones Internas:")
    print("  - UI Usuario: http://localhost:8000/user-notifications")
    print("  - API:        http://localhost:8000/api/internal-notifications")
    print("\nDocumentacion:")
    print("  - Swagger UI: http://localhost:8000/docs")
    print("  - ReDoc:      http://localhost:8000/redoc")
    print("  - OpenAPI:    http://localhost:8000/openapi.json")
    print("\n" + "=" * 60)
    print("Servidor iniciado en http://localhost:8000")
    print("Presiona Ctrl+C para detener")
    print("=" * 60 + "\n")

    # Ejecutar servidor con Uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
