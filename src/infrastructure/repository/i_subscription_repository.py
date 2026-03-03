"""
Interfaz para repositorio de suscripciones de notificaciones
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.subscription import UserNotificationSubscription


class ISubscriptionRepository(ABC):
    """
    Interfaz para repositorio de preferencias de notificación de usuarios

    Responsabilidad: Gestionar las preferencias de cada usuario sobre qué
    tipos de notificaciones quiere recibir y por cuáles canales
    (email, SMS, WhatsApp) para cada tipo de evento
    """

    @abstractmethod
    def save(self, subscription: UserNotificationSubscription) -> UserNotificationSubscription:
        """
        Guarda o actualiza una suscripción/preferencia de notificación

        Args:
            subscription: Preferencia de notificación a guardar

        Returns:
            Suscripción guardada con ID asignado
        """
        pass

    @abstractmethod
    def find_by_user(self, user_id: str) -> List[UserNotificationSubscription]:
        """
        Obtiene todas las preferencias de notificación de un usuario

        Args:
            user_id: ID del usuario

        Returns:
            Lista de preferencias ordenadas por tipo de evento
        """
        pass

    @abstractmethod
    def find_by_user_and_event(self, user_id: str, event_type: str) -> Optional[UserNotificationSubscription]:
        """
        Obtiene la preferencia de un usuario para un evento específico

        Args:
            user_id: ID del usuario
            event_type: Tipo de evento

        Returns:
            Preferencia de notificación o None si no existe
        """
        pass

    @abstractmethod
    def delete(self, user_id: str, event_type: str) -> bool:
        """
        Elimina una preferencia de notificación

        Args:
            user_id: ID del usuario
            event_type: Tipo de evento

        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        pass
