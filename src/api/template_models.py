"""
Modelos Pydantic para validación de API de templates y generación de OpenAPI schemas
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field, field_validator


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
