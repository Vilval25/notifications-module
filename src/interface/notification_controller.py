from typing import List, Dict, Any
from ..business.notification_service import NotificationService
from ..domain.notification_log import NotificationLog
from .notification_request import NotificationRequest


class NotificationController:
    """Controlador para gestionar las notificaciones"""

    def __init__(self, notification_service: NotificationService):
        self._notification_service = notification_service

    def send_notification(self, request: NotificationRequest) -> Dict[str, Any]:
        """
        Envía una notificación

        Args:
            request: Datos de la notificación a enviar

        Returns:
            Diccionario con el resultado de la operación
        """
        try:
            self._notification_service.process_notification(request)
            return {
                "status": "success",
                "message": "Notificación enviada correctamente"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }

    def get_logs(self) -> List[NotificationLog]:
        """
        Obtiene todos los logs de notificaciones

        Returns:
            Lista de logs de notificaciones
        """
        return self._notification_service.get_all_logs()
