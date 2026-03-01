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


class EventTypeEnum(str, Enum):
    """Enum de tipos de eventos para notificaciones"""
    TRAMITE_OBSERVADO = "tramite_observado"
    TRAMITE_APROBADO = "tramite_aprobado"
    TRAMITE_RECHAZADO = "tramite_rechazado"
    CONFIRMACION_CAMBIO_PASSWORD = "confirmacion_cambio_password"
    COMPROBANTE_PAGO = "comprobante_pago"
    CREACION_CUENTA = "creacion_cuenta"


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
    event_type: EventTypeEnum = Field(
        ...,
        description="Tipo de evento que dispara la notificación. El sistema usará la plantilla activa para este evento.",
        examples=["tramite_aprobado", "creacion_cuenta"]
    )
    params: Dict[str, Any] = Field(
        ...,
        description="Parámetros para renderizar la plantilla (nombre, email, enlace, telefono, etc.)",
        examples=[{
            "nombre": "Juan Pérez",
            "email": "juan@ejemplo.com",
            "enlace": "https://campus360.com/tramite/123",
            "telefono": "+51 999 999 999",
            "source_module": "TRAMITES"
        }]
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "recipient": "usuario@ejemplo.com",
                    "channel": "email",
                    "event_type": "tramite_aprobado",
                    "params": {
                        "nombre": "Juan Pérez",
                        "email": "juan@ejemplo.com",
                        "enlace": "https://campus360.com/tramite/123",
                        "telefono": "+51 999 999 999",
                        "source_module": "TRAMITES"
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
