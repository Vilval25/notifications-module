"""
Interfaz para repositorio de notificaciones internas
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.internal_notification import InternalNotification


class IInternalNotificationRepository(ABC):
    """
    Interfaz para repositorio de notificaciones internas del sistema

    Responsabilidad: Gestionar las notificaciones que aparecen en el panel
    del usuario dentro de la aplicación (no son emails/SMS/WhatsApp)
    """

    @abstractmethod
    def save(self, notification: InternalNotification) -> InternalNotification:
        """
        Guarda una nueva notificación interna

        Args:
            notification: Notificación a guardar

        Returns:
            Notificación guardada con ID asignado
        """
        pass

    @abstractmethod
    def find_by_user(self, user_id: str, limit: Optional[int] = None,
                     only_unread: bool = False) -> List[InternalNotification]:
        """
        Obtiene las notificaciones de un usuario

        Args:
            user_id: ID del usuario
            limit: Límite de resultados (opcional)
            only_unread: Si True, solo retorna notificaciones no leídas

        Returns:
            Lista de notificaciones ordenadas por fecha descendente
        """
        pass

    @abstractmethod
    def find_by_id(self, notification_id: int) -> Optional[InternalNotification]:
        """
        Obtiene una notificación por su ID

        Args:
            notification_id: ID de la notificación

        Returns:
            Notificación o None si no existe
        """
        pass

    @abstractmethod
    def mark_as_read(self, notification_id: int) -> bool:
        """
        Marca una notificación como leída

        Args:
            notification_id: ID de la notificación

        Returns:
            True si se actualizó correctamente, False en caso contrario
        """
        pass

    @abstractmethod
    def mark_all_as_read(self, user_id: str) -> int:
        """
        Marca todas las notificaciones de un usuario como leídas

        Args:
            user_id: ID del usuario

        Returns:
            Número de notificaciones actualizadas
        """
        pass

    @abstractmethod
    def count_unread(self, user_id: str) -> int:
        """
        Cuenta las notificaciones no leídas de un usuario

        Args:
            user_id: ID del usuario

        Returns:
            Número de notificaciones no leídas
        """
        pass

    @abstractmethod
    def delete(self, notification_id: int) -> bool:
        """
        Elimina una notificación

        Args:
            notification_id: ID de la notificación

        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        pass

    @abstractmethod
    def delete_old_notifications(self, user_id: str, days: int = 30) -> int:
        """
        Elimina notificaciones antiguas de un usuario

        Args:
            user_id: ID del usuario
            days: Días de antigüedad para eliminar (default: 30)

        Returns:
            Número de notificaciones eliminadas
        """
        pass
