from abc import ABC, abstractmethod
from typing import List
from ...domain.notification_log import NotificationLog


class INotificationLogRepository(ABC):
    """
    Interfaz para repositorio de logs de notificaciones enviadas

    Responsabilidad: Persistir el historial/auditoría de todas las notificaciones
    enviadas por el sistema (email, SMS, WhatsApp)
    """

    @abstractmethod
    def save(self, log: NotificationLog) -> None:
        """
        Persiste un log de notificación enviada

        Args:
            log: Log de notificación a guardar
        """
        pass

    @abstractmethod
    def find_by_module(self, module_id: str) -> List[NotificationLog]:
        """
        Busca logs de notificaciones por módulo de origen

        Args:
            module_id: ID del módulo de origen (vacío para obtener todos)

        Returns:
            Lista de logs de notificaciones
        """
        pass
