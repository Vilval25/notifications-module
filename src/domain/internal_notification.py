"""
Entidad de dominio para notificaciones internas del sistema
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class InternalNotification:
    """
    Representa una notificación interna del sistema para mostrar en el panel de usuario

    Attributes:
        id: Identificador único de la notificación
        user_id: ID del usuario destinatario
        solicitud_id: ID de la solicitud/trámite relacionado
        event_type: Tipo de evento (tramite_registrado, tramite_aprobado, etc.)
        notification_subject: Asunto de la notificación
        solicitud_subject: Asunto de la solicitud/trámite
        is_read: Si la notificación ha sido leída
        created_at: Fecha y hora de creación
        solicitud_url: URL para ir a la solicitud (opcional)
    """

    user_id: str
    solicitud_id: str
    event_type: str
    notification_subject: str
    solicitud_subject: str
    is_read: bool = False
    created_at: datetime = None
    id: Optional[int] = None
    solicitud_url: Optional[str] = None

    def __post_init__(self):
        """Inicializa valores por defecto"""
        if self.created_at is None:
            self.created_at = datetime.now()

    def mark_as_read(self):
        """Marca la notificación como leída"""
        self.is_read = True

    def to_dict(self):
        """Convierte la entidad a diccionario"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'solicitud_id': self.solicitud_id,
            'event_type': self.event_type,
            'notification_subject': self.notification_subject,
            'solicitud_subject': self.solicitud_subject,
            'is_read': self.is_read,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'solicitud_url': self.solicitud_url
        }
