from enum import Enum


class NotificationChannel(Enum):
    """Enum para definir tipos de canales de notificación"""
    EMAIL = "email"
    SMS = "sms"
    WHATSAPP = "whatsapp"
