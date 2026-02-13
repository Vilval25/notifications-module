from datetime import datetime
from dataclasses import dataclass
from typing import Optional
from .notification_channel import NotificationChannel


@dataclass
class NotificationLog:
    """Modelo de dominio para registro de notificaciones"""
    recipient: str
    channel: NotificationChannel
    content: str
    status: str
    source_module: str
    timestamp: datetime = None
    id: Optional[int] = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
