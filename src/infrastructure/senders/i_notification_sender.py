from abc import ABC, abstractmethod


class INotificationSender(ABC):
    """Interfaz para senders de notificaciones"""

    @abstractmethod
    def send(self, to: str, body: str) -> bool:
        """
        Envía una notificación

        Args:
            to: Destinatario
            body: Contenido del mensaje

        Returns:
            True si se envió correctamente, False en caso contrario
        """
        pass
