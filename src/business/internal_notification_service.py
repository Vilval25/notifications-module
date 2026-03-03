"""
Servicio de negocio para gestión de notificaciones internas
"""

from typing import List, Optional, Dict, Any
from src.domain.internal_notification import InternalNotification
from src.infrastructure.repository.sql_internal_notification_repository import InternalNotificationRepository


class InternalNotificationService:
    """
    Servicio para gestionar notificaciones internas del sistema

    Proporciona lógica de negocio para crear, leer, actualizar y eliminar
    notificaciones que se muestran en el panel de usuario
    """

    def __init__(self, repository: InternalNotificationRepository):
        """
        Inicializa el servicio

        Args:
            repository: Repositorio de notificaciones internas
        """
        self._repository = repository

    def create_notification_from_event(self, event_data: Dict[str, Any]) -> InternalNotification:
        """
        Crea una notificación interna a partir de un evento de trámite

        Args:
            event_data: Datos del evento que debe incluir:
                - user_id: ID del usuario destinatario
                - solicitud_id: ID de la solicitud/trámite
                - event_type: Tipo de evento (tramite_registrado, tramite_aprobado, etc.)
                - notification_subject: Asunto de la notificación
                - solicitud_subject: Asunto de la solicitud
                - solicitud_url: URL para ir a la solicitud (opcional)

        Returns:
            Notificación creada con ID asignado

        Raises:
            ValueError: Si faltan campos requeridos
        """
        required_fields = [
            'user_id', 'solicitud_id', 'event_type',
            'notification_subject', 'solicitud_subject'
        ]

        for field in required_fields:
            if field not in event_data:
                raise ValueError(f"Campo requerido faltante: {field}")

        notification = InternalNotification(
            user_id=event_data['user_id'],
            solicitud_id=event_data['solicitud_id'],
            event_type=event_data['event_type'],
            notification_subject=event_data['notification_subject'],
            solicitud_subject=event_data['solicitud_subject'],
            solicitud_url=event_data.get('solicitud_url')
        )

        return self._repository.save(notification)

    def get_user_notifications(self, user_id: str, limit: Optional[int] = None,
                               only_unread: bool = False) -> List[InternalNotification]:
        """
        Obtiene las notificaciones de un usuario

        Args:
            user_id: ID del usuario
            limit: Número máximo de notificaciones a retornar
            only_unread: Si True, solo retorna notificaciones no leídas

        Returns:
            Lista de notificaciones ordenadas por fecha descendente
        """
        return self._repository.find_by_user(user_id, limit, only_unread)

    def get_notification_by_id(self, notification_id: int) -> Optional[InternalNotification]:
        """
        Obtiene una notificación específica por ID

        Args:
            notification_id: ID de la notificación

        Returns:
            Notificación o None si no existe
        """
        return self._repository.find_by_id(notification_id)

    def mark_as_read(self, notification_id: int) -> bool:
        """
        Marca una notificación como leída

        Args:
            notification_id: ID de la notificación

        Returns:
            True si se marcó correctamente, False en caso contrario
        """
        return self._repository.mark_as_read(notification_id)

    def mark_all_as_read(self, user_id: str) -> int:
        """
        Marca todas las notificaciones de un usuario como leídas

        Args:
            user_id: ID del usuario

        Returns:
            Número de notificaciones marcadas
        """
        return self._repository.mark_all_as_read(user_id)

    def get_unread_count(self, user_id: str) -> int:
        """
        Obtiene el número de notificaciones no leídas de un usuario

        Args:
            user_id: ID del usuario

        Returns:
            Número de notificaciones no leídas
        """
        return self._repository.count_unread(user_id)

    def delete_notification(self, notification_id: int) -> bool:
        """
        Elimina una notificación

        Args:
            notification_id: ID de la notificación

        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        return self._repository.delete(notification_id)

    def cleanup_old_notifications(self, user_id: str, days: int = 30) -> int:
        """
        Limpia notificaciones antiguas de un usuario

        Args:
            user_id: ID del usuario
            days: Días de antigüedad para eliminar (default: 30)

        Returns:
            Número de notificaciones eliminadas
        """
        return self._repository.delete_old_notifications(user_id, days)

    def get_notification_summary(self, user_id: str) -> Dict[str, Any]:
        """
        Obtiene un resumen de las notificaciones del usuario

        Args:
            user_id: ID del usuario

        Returns:
            Dict con estadísticas: total, unread, recent
        """
        all_notifications = self._repository.find_by_user(user_id)
        unread_count = self._repository.count_unread(user_id)
        recent = self._repository.find_by_user(user_id, limit=5)

        return {
            'total': len(all_notifications),
            'unread': unread_count,
            'recent': [n.to_dict() for n in recent]
        }
