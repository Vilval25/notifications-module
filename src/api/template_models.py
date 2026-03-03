"""
Modelos Pydantic para validación de API de templates y generación de OpenAPI schemas
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, field_validator
from enum import Enum


class TemplateListResponse(BaseModel):
    """Lista de plantillas disponibles"""
    templates: List[str] = Field(
        ...,
        description="Lista de nombres de plantillas sin extensión .hbs"
    )
    total: int = Field(..., description="Total de plantillas")

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "templates": ["welcome", "notification"],
                "total": 2
            }]
        }
    }


class TemplateDetailResponse(BaseModel):
    """Detalle de una plantilla"""
    name: str = Field(..., description="Nombre de la plantilla sin extensión")
    content: str = Field(..., description="Contenido Handlebars de la plantilla")
    size: int = Field(..., description="Tamaño del archivo en bytes")
    modified: str = Field(..., description="Última modificación en ISO format")

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "name": "welcome",
                "content": "<h1>¡Bienvenido {{name}}!</h1>",
                "size": 142,
                "modified": "2026-02-20T10:30:00"
            }]
        }
    }


class TemplateCreateRequest(BaseModel):
    """Request para crear una plantilla"""
    name: str = Field(
        ...,
        description="Nombre de la plantilla (sin extensión .hbs)",
        min_length=1,
        max_length=100
    )
    content: str = Field(
        ...,
        description="Contenido Handlebars de la plantilla",
        min_length=1
    )

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        # Validar que no contenga caracteres inválidos para nombres de archivo
        invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        if any(char in v for char in invalid_chars):
            raise ValueError(f"El nombre no puede contener: {', '.join(invalid_chars)}")
        if v.endswith('.hbs'):
            raise ValueError("No incluyas la extensión .hbs en el nombre")
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "name": "password_reset",
                "content": "<h1>Restablecer contraseña</h1>\n<p>Hola {{name}},</p>"
            }]
        }
    }


class TemplateUpdateRequest(BaseModel):
    """Request para actualizar una plantilla"""
    content: str = Field(
        ...,
        description="Nuevo contenido Handlebars de la plantilla",
        min_length=1
    )

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "content": "<h1>¡Bienvenido {{name}}!</h1>\n<p>Contenido actualizado</p>"
            }]
        }
    }


class TemplatePreviewRequest(BaseModel):
    """Request para preview de plantilla"""
    content: str = Field(
        ...,
        description="Contenido Handlebars a renderizar"
    )
    params: Dict[str, Any] = Field(
        default_factory=dict,
        description="Parámetros de prueba para renderizar la plantilla"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "content": "<h1>Hola {{name}}!</h1>",
                "params": {
                    "name": "Juan Pérez"
                }
            }]
        }
    }


class TemplatePreviewResponse(BaseModel):
    """Response del preview"""
    rendered: str = Field(..., description="HTML renderizado")
    valid: bool = Field(..., description="Si la plantilla es válida")
    error: Optional[str] = Field(None, description="Mensaje de error si hay")

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "rendered": "<h1>Hola Juan Pérez!</h1>",
                "valid": True,
                "error": None
            }]
        }
    }


class TemplateValidationResponse(BaseModel):
    """Response de validación de sintaxis"""
    valid: bool = Field(..., description="Si la sintaxis es válida")
    error: Optional[str] = Field(None, description="Mensaje de error si hay")

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "valid": True,
                "error": None
            }]
        }
    }


class TemplateDeleteResponse(BaseModel):
    """Response al eliminar plantilla"""
    status: str = Field(..., description="Estado de la operación")
    message: str = Field(..., description="Mensaje descriptivo")

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "status": "success",
                "message": "Plantilla 'welcome' eliminada correctamente"
            }]
        }
    }


# ========================================
# Nuevos modelos para sistema de eventos
# ========================================

class EventType(str, Enum):
    """Tipos de eventos del sistema"""
    TRAMITE_REGISTRADO = "tramite_registrado"
    TRAMITE_OBSERVADO = "tramite_observado"
    TRAMITE_APROBADO = "tramite_aprobado"
    TRAMITE_RECHAZADO = "tramite_rechazado"
    CONFIRMACION_CAMBIO_PASSWORD = "confirmacion_cambio_password"
    COMPROBANTE_PAGO = "comprobante_pago"
    CREACION_CUENTA = "creacion_cuenta"


class TemplateWithStatusResponse(BaseModel):
    """Plantilla con metadata y estado"""
    name: str = Field(..., description="Nombre de la plantilla sin extensión")
    subject: str = Field(..., description="Asunto del email")
    event_type: Optional[EventType] = Field(None, description="Tipo de evento asignado")
    is_active: bool = Field(..., description="Si la plantilla está activa")
    modified: str = Field(..., description="Última modificación en ISO format")

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "name": "bienvenida",
                "subject": "Bienvenido a Campus360",
                "event_type": "tramite_aprobado",
                "is_active": True,
                "modified": "2026-02-27T10:30:00"
            }]
        }
    }


class TemplateListWithStatusResponse(BaseModel):
    """Lista de plantillas con estado"""
    templates: List[TemplateWithStatusResponse] = Field(
        ...,
        description="Lista de plantillas con metadata y estado"
    )
    total: int = Field(..., description="Total de plantillas")

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "templates": [
                    {
                        "name": "bienvenida",
                        "subject": "Bienvenido a Campus360",
                        "event_type": "tramite_aprobado",
                        "is_active": True,
                        "modified": "2026-02-27T10:30:00"
                    }
                ],
                "total": 1
            }]
        }
    }


class TemplateCreateRequestNew(BaseModel):
    """Request para crear plantilla con metadata"""
    name: str = Field(
        ...,
        description="Nombre de la plantilla (sin extensión .hbs)",
        min_length=1,
        max_length=100
    )
    subject: str = Field(
        ...,
        description="Asunto del email",
        min_length=1,
        max_length=200
    )
    event_type: EventType = Field(
        ...,
        description="Tipo de evento al que pertenece la plantilla"
    )
    content: str = Field(
        ...,
        description="Contenido Handlebars de la plantilla",
        min_length=1
    )

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        if any(char in v for char in invalid_chars):
            raise ValueError(f"El nombre no puede contener: {', '.join(invalid_chars)}")
        if v.endswith('.hbs'):
            raise ValueError("No incluyas la extensión .hbs en el nombre")
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "name": "tramite_aprobado_notif",
                "subject": "Tu trámite ha sido aprobado",
                "event_type": "tramite_aprobado",
                "content": "<h1>¡Hola {{nombre}}!</h1>\n<p>Tu trámite ha sido aprobado.</p>"
            }]
        }
    }


class TemplateUpdateRequestNew(BaseModel):
    """Request para actualizar plantilla con subject, event_type y nombre opcional"""
    new_name: Optional[str] = Field(
        None,
        description="Nuevo nombre de la plantilla (opcional, para renombrar)",
        min_length=1,
        max_length=100
    )
    subject: str = Field(
        ...,
        description="Nuevo asunto del email",
        min_length=1,
        max_length=200
    )
    content: str = Field(
        ...,
        description="Nuevo contenido Handlebars de la plantilla",
        min_length=1
    )
    event_type: Optional[EventType] = Field(
        None,
        description="Tipo de evento (solo se puede cambiar si la plantilla no está activa)"
    )

    @field_validator('new_name')
    @classmethod
    def validate_new_name(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        if any(char in v for char in invalid_chars):
            raise ValueError(f"El nombre no puede contener: {', '.join(invalid_chars)}")
        if v.endswith('.hbs'):
            raise ValueError("No incluyas la extensión .hbs en el nombre")
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "new_name": "tramite_aprobado_v2",
                "subject": "Bienvenido a la plataforma",
                "content": "<h1>¡Hola {{nombre}}!</h1>\n<p>Contenido actualizado</p>",
                "event_type": "tramite_aprobado"
            }]
        }
    }


class TemplateDetailResponseNew(BaseModel):
    """Detalle completo de una plantilla con metadata"""
    name: str = Field(..., description="Nombre de la plantilla sin extensión")
    subject: str = Field(..., description="Asunto del email")
    event_type: Optional[EventType] = Field(None, description="Tipo de evento asignado")
    content: str = Field(..., description="Contenido Handlebars de la plantilla")
    is_active: bool = Field(..., description="Si la plantilla está activa")
    size: int = Field(..., description="Tamaño del archivo en bytes")
    modified: str = Field(..., description="Última modificación en ISO format")

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "name": "bienvenida",
                "subject": "Bienvenido a Campus360",
                "event_type": "tramite_aprobado",
                "content": "<h1>¡Hola {{nombre}}!</h1>",
                "is_active": True,
                "size": 142,
                "modified": "2026-02-27T10:30:00"
            }]
        }
    }


class EventResponse(BaseModel):
    """Evento con plantilla asignada"""
    event_type: EventType = Field(..., description="Tipo de evento")
    template_name: str = Field(..., description="Nombre de la plantilla activa")
    is_active: bool = Field(..., description="Si está activa")

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "event_type": "tramite_aprobado",
                "template_name": "bienvenida",
                "is_active": True
            }]
        }
    }


class EventListResponse(BaseModel):
    """Lista de eventos con plantillas"""
    events: List[EventResponse] = Field(..., description="Lista de eventos")
    total: int = Field(..., description="Total de eventos")

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "events": [
                    {
                        "event_type": "tramite_aprobado",
                        "template_name": "bienvenida",
                        "is_active": True
                    }
                ],
                "total": 1
            }]
        }
    }


class ActivateEventRequest(BaseModel):
    """Request para activar una plantilla para un evento"""
    template_name: str = Field(
        ...,
        description="Nombre de la plantilla a activar",
        min_length=1
    )

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "template_name": "bienvenida"
            }]
        }
    }
