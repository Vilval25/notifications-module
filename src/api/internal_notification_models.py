"""
Modelos Pydantic para API de notificaciones internas
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class InternalNotificationCreateRequest(BaseModel):
    """Request para crear una notificación interna"""
    user_id: str = Field(
        ...,
        description="ID del usuario destinatario",
        examples=["user123"]
    )
    solicitud_id: str = Field(
        ...,
        description="ID de la solicitud/trámite",
        examples=["SOL-2024-001"]
    )
    event_type: str = Field(
        ...,
        description="Tipo de evento (tramite_registrado, tramite_aprobado, etc.)",
        examples=["tramite_aprobado"]
    )
    notification_subject: str = Field(
        ...,
        description="Asunto de la notificación",
        examples=["Trámite aprobado"]
    )
    solicitud_subject: str = Field(
        ...,
        description="Asunto de la solicitud",
        examples=["Solicitud de certificado de estudios"]
    )
    solicitud_url: Optional[str] = Field(
        None,
        description="URL para ir a la solicitud",
        examples=["https://campus360.com/tramites/SOL-2024-001"]
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "user_id": "user123",
                    "solicitud_id": "SOL-2024-001",
                    "event_type": "tramite_aprobado",
                    "notification_subject": "Trámite aprobado",
                    "solicitud_subject": "Solicitud de certificado de estudios",
                    "solicitud_url": "https://campus360.com/tramites/SOL-2024-001"
                }
            ]
        }
    }


class InternalNotificationResponse(BaseModel):
    """Response con datos de una notificación interna"""
    id: int = Field(..., description="ID de la notificación")
    user_id: str = Field(..., description="ID del usuario")
    solicitud_id: str = Field(..., description="ID de la solicitud")
    event_type: str = Field(..., description="Tipo de evento")
    notification_subject: str = Field(..., description="Asunto de la notificación")
    solicitud_subject: str = Field(..., description="Asunto de la solicitud")
    is_read: bool = Field(..., description="Si la notificación ha sido leída")
    created_at: str = Field(..., description="Fecha de creación en formato ISO")
    solicitud_url: Optional[str] = Field(None, description="URL de la solicitud")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "user_id": "user123",
                    "solicitud_id": "SOL-2024-001",
                    "event_type": "tramite_aprobado",
                    "notification_subject": "Trámite aprobado",
                    "solicitud_subject": "Solicitud de certificado de estudios",
                    "is_read": False,
                    "created_at": "2024-03-01T10:30:00",
                    "solicitud_url": "https://campus360.com/tramites/SOL-2024-001"
                }
            ]
        }
    }


class InternalNotificationListResponse(BaseModel):
    """Response con lista de notificaciones internas"""
    total: int = Field(..., description="Número total de notificaciones")
    unread: int = Field(..., description="Número de notificaciones no leídas")
    notifications: List[InternalNotificationResponse] = Field(
        ...,
        description="Lista de notificaciones"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "total": 10,
                    "unread": 3,
                    "notifications": [
                        {
                            "id": 1,
                            "user_id": "user123",
                            "solicitud_id": "SOL-2024-001",
                            "event_type": "tramite_aprobado",
                            "notification_subject": "Trámite aprobado",
                            "solicitud_subject": "Solicitud de certificado",
                            "is_read": False,
                            "created_at": "2024-03-01T10:30:00",
                            "solicitud_url": "https://campus360.com/tramites/SOL-2024-001"
                        }
                    ]
                }
            ]
        }
    }


class MarkAsReadRequest(BaseModel):
    """Request para marcar notificación como leída"""
    notification_id: int = Field(
        ...,
        description="ID de la notificación a marcar como leída"
    )


class MarkAsReadResponse(BaseModel):
    """Response al marcar como leída"""
    status: str = Field(..., description="Estado de la operación")
    message: str = Field(..., description="Mensaje descriptivo")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "status": "success",
                    "message": "Notificación marcada como leída"
                }
            ]
        }
    }


class UnreadCountResponse(BaseModel):
    """Response con contador de notificaciones no leídas"""
    unread_count: int = Field(..., description="Número de notificaciones no leídas")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"unread_count": 5}
            ]
        }
    }


class NotificationSummaryResponse(BaseModel):
    """Response con resumen de notificaciones del usuario"""
    total: int = Field(..., description="Total de notificaciones")
    unread: int = Field(..., description="Notificaciones no leídas")
    recent: List[dict] = Field(..., description="Notificaciones recientes (últimas 5)")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "total": 25,
                    "unread": 5,
                    "recent": []
                }
            ]
        }
    }
