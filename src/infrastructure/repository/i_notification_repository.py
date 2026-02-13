from abc import ABC, abstractmethod
from typing import List
from ...domain.notification_log import NotificationLog


class INotificationRepository(ABC):
    """Interfaz para repositorio de logs de notificaciones"""

    @abstractmethod
    def save(self, log: NotificationLog) -> None:
        """
        Persiste un log de notificación

        Args:
            log: Log a guardar
        """
        pass

    @abstractmethod
    def find_by_module(self, module_id: str) -> List[NotificationLog]:
        """
        Busca logs por módulo de origen

        Args:
            module_id: ID del módulo (vacío para todos)

        Returns:
            Lista de logs
        """
        pass
