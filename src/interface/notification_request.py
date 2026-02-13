from dataclasses import dataclass
from typing import Dict, Any
from ..domain.notification_channel import NotificationChannel


@dataclass
class NotificationRequest:
    """Request para enviar notificaciones"""
    recipient: str
    channel: NotificationChannel
    template_name: str
    params: Dict[str, Any]
