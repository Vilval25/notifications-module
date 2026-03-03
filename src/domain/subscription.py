"""
Entidad de dominio para suscripciones de notificaciones de usuario
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class UserNotificationSubscription:
    """
    Representa una suscripción de un usuario a notificaciones de un evento específico
    """
    user_id: str
    event_type: str
    email_enabled: bool = False
    sms_enabled: bool = False
    whatsapp_enabled: bool = False
    created_at: datetime = None
    updated_at: datetime = None
    id: Optional[int] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()
