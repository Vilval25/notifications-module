from typing import List
from ..domain.notification_log import NotificationLog
from ..infrastructure.repository.i_notification_log_repository import INotificationLogRepository
from .i_template_engine import ITemplateEngine
from .sender_factory import SenderFactory


class NotificationService:
    """Servicio principal para procesamiento de notificaciones"""

    def __init__(self, template_engine: ITemplateEngine, sender_factory: SenderFactory,
                 repository: INotificationLogRepository):
        """
        Inicializa el servicio de notificaciones

        Args:
            template_engine: Motor de plantillas
            sender_factory: Fábrica de senders
            repository: Repositorio de logs de notificaciones
        """
        self._template_engine = template_engine
        self._sender_factory = sender_factory
        self._repository = repository

    def process_notification(self, request) -> None:
        """
        Procesa y envía una notificación

        Args:
            request: Datos de la notificación (NotificationRequest)
        """
        success = False
        content = ""
        error_msg = None

        try:
            print(f"\n[NOTIF] Procesando notificación:")
            print(f"   Canal: {request.channel.value}")
            print(f"   Destinatario: {request.recipient}")
            print(f"   Plantilla: {request.template_name}")

            # Renderizar plantilla
            content = self._template_engine.render(request.template_name, request.params)

            # Obtener sender apropiado
            sender = self._sender_factory.get_sender(request.channel)

            # Enviar notificación
            success = sender.send(request.recipient, content)

        except Exception as e:
            error_msg = f"{type(e).__name__}: {e}"
            print(f"   [ERROR] Error procesando notificación: {error_msg}")
            success = False

        # Crear log
        log = NotificationLog(
            recipient=request.recipient,
            channel=request.channel,
            content=content if content else f"Error: {error_msg}",
            status="SUCCESS" if success else "FAILED",
            source_module=request.params.get("source_module", "UNKNOWN")
        )

        # Guardar log
        self._repository.save(log)

        if success:
            print(f"   [OK] Notificación procesada exitosamente\n")
        else:
            print(f"   [FAILED] Notificación falló\n")

    def get_all_logs(self) -> List[NotificationLog]:
        """
        Obtiene todos los logs de notificaciones

        Returns:
            Lista de logs
        """
        return self._repository.find_by_module("")
