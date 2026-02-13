"""
Modelos Pydantic para validación de API y generación de OpenAPI schemas
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from enum import Enum


class ChannelEnum(str, Enum):
    """Enum de canales de notificación para API"""
    EMAIL = "email"
    SMS = "sms"
    WHATSAPP = "whatsapp"


class NotificationSendRequest(BaseModel):
    """Request para enviar notificación"""
    recipient: str = Field(
        ...,
        description="Destinatario de la notificación (email, teléfono, etc.)",
        examples=["usuario@ejemplo.com", "+1234567890"]
    )
    channel: ChannelEnum = Field(
        ...,
        description="Canal de envío de la notificación"
    )
    template_name: str = Field(
        ...,
        description="Nombre de la plantilla a utilizar (sin extensión)",
        examples=["welcome", "notification"]
    )
    params: Dict[str, Any] = Field(
        ...,
        description="Parámetros para renderizar la plantilla",
        examples=[{
            "name": "Juan Pérez",
            "source_module": "USER_REGISTRATION"
        }]
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "recipient": "usuario@ejemplo.com",
                    "channel": "email",
                    "template_name": "welcome",
                    "params": {
                        "name": "Juan Pérez",
                        "source_module": "USER_REGISTRATION"
                    }
                }
            ]
        }
    }


class NotificationSendResponse(BaseModel):
    """Response al enviar notificación"""
    status: str = Field(
        ...,
        description="Estado de la operación: 'success' o 'error'"
    )
    message: str = Field(
        ...,
        description="Mensaje descriptivo del resultado"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "status": "success",
                    "message": "Notificación enviada correctamente"
                }
            ]
        }
    }


class NotificationLogResponse(BaseModel):
    """Modelo de log de notificación para respuesta"""
    id: Optional[int] = Field(None, description="ID del log")
    recipient: str = Field(..., description="Destinatario")
    channel: str = Field(..., description="Canal utilizado")
    content: str = Field(..., description="Contenido enviado (truncado si es muy largo)")
    status: str = Field(..., description="Estado: SUCCESS o FAILED")
    timestamp: str = Field(..., description="Fecha y hora en formato ISO")
    source_module: str = Field(..., description="Módulo de origen")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": 1,
                    "recipient": "usuario@ejemplo.com",
                    "channel": "email",
                    "content": "<h1>¡Bienvenido Juan Pérez!</h1>...",
                    "status": "SUCCESS",
                    "timestamp": "2024-01-15T10:30:00",
                    "source_module": "USER_REGISTRATION"
                }
            ]
        }
    }


class NotificationLogsResponse(BaseModel):
    """Response para lista de logs"""
    total: int = Field(..., description="Número total de logs")
    logs: List[NotificationLogResponse] = Field(..., description="Lista de logs")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "total": 2,
                    "logs": [
                        {
                            "id": 1,
                            "recipient": "usuario@ejemplo.com",
                            "channel": "email",
                            "content": "<h1>¡Bienvenido!</h1>...",
                            "status": "SUCCESS",
                            "timestamp": "2024-01-15T10:30:00",
                            "source_module": "TEST"
                        }
                    ]
                }
            ]
        }
    }


class HealthResponse(BaseModel):
    """Response del endpoint de salud"""
    status: str = Field(..., description="Estado del servicio")

    model_config = {
        "json_schema_extra": {
            "examples": [{"status": "healthy"}]
        }
    }


class APIInfoResponse(BaseModel):
    """Response con información de la API"""
    message: str = Field(..., description="Mensaje de bienvenida")
    version: str = Field(..., description="Versión de la API")
    endpoints: Dict[str, str] = Field(..., description="Endpoints disponibles")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "message": "API de Notificaciones",
                    "version": "1.0",
                    "endpoints": {
                        "POST /api/notifications/send": "Enviar una notificación",
                        "GET /api/notifications/logs": "Obtener logs de notificaciones",
                        "GET /health": "Estado de la API"
                    }
                }
            ]
        }
    }


class ErrorResponse(BaseModel):
    """Response de error"""
    error: str = Field(..., description="Mensaje de error")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"error": "Campo requerido: recipient"}
            ]
        }
    }
