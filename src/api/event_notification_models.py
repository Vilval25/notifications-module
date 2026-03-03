"""
Modelos Pydantic para endpoints de eventos unificados
"""
from pydantic import BaseModel, Field
from typing import Optional


class TramiteEventRequest(BaseModel):
    """
    Request para eventos de trámites.

    El sistema creará automáticamente:
    - Notificación interna (siempre aparecerá en el panel del usuario)
    - Notificaciones externas según preferencias del usuario (email, SMS, WhatsApp)

    **Nota:** Los datos de ejemplo (IDs, URLs, teléfonos) son ficticios y solo con fines demostrativos.
    """
    # Datos del usuario
    user_id: str = Field(..., description="ID del usuario")
    user_email: str = Field(..., description="Email del usuario")
    user_name: str = Field(..., description="Nombre del usuario")
    user_phone: Optional[str] = Field(None, description="Teléfono del usuario")

    # Datos del trámite
    solicitud_id: str = Field(..., description="ID de la solicitud/trámite (ejemplo: 'SOL-2024-001')")
    event_type: str = Field(..., description="Tipo de evento: tramite_registrado | tramite_observado | tramite_aprobado | tramite_rechazado")
    solicitud_subject: str = Field(..., description="Asunto/descripción de la solicitud")
    solicitud_url: Optional[str] = Field(None, description="URL para ver la solicitud (ejemplo: 'https://campus360.com/tramites/SOL-2024-001' - no es una URL real)")

    # Metadatos opcionales
    source_module: Optional[str] = Field(None, description="Módulo de origen que genera el evento (ejemplo: 'TRAMITES', 'ACADEMICO', 'BIBLIOTECA')")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "user_id": "user_demo",
                    "user_email": "juan.perez@ejemplo.com",
                    "user_name": "Juan Pérez",
                    "user_phone": "+51999888777",
                    "solicitud_id": "SOL-2024-001",
                    "event_type": "tramite_aprobado",
                    "solicitud_subject": "Solicitud de Certificado de Estudios",
                    "solicitud_url": "https://campus360.com/tramites/SOL-2024-001",
                    "source_module": "TRAMITES"
                }
            ]
        }
    }


class CreacionCuentaEventRequest(BaseModel):
    """
    Request para evento de creación de cuenta.

    Solo envía email de bienvenida/activación al nuevo usuario.
    No crea notificación interna ni verifica preferencias.

    **Nota:** Los datos de ejemplo (emails, URLs de activación, contraseñas) son ficticios y solo con fines demostrativos.
    """
    user_email: str = Field(..., description="Email del nuevo usuario")
    user_name: str = Field(..., description="Nombre del nuevo usuario")
    activation_url: Optional[str] = Field(None, description="URL de activación de cuenta (ejemplo: 'https://campus360.com/activate/abc123' - no es una URL real)")
    temporary_password: Optional[str] = Field(None, description="Contraseña temporal generada para el usuario")

    # Metadatos opcionales
    source_module: Optional[str] = Field(None, description="Módulo de origen que genera el evento (ejemplo: 'USER_REGISTRATION', 'AUTH', 'ADMIN')")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "user_email": "maria.garcia@ejemplo.com",
                    "user_name": "María García",
                    "activation_url": "https://campus360.com/activate/abc123def456",
                    "temporary_password": "Temp1234",
                    "source_module": "USER_REGISTRATION"
                }
            ]
        }
    }


class CambioContrasenaEventRequest(BaseModel):
    """
    Request para evento de cambio/reseteo de contraseña.

    Solo envía email con el enlace o código de reseteo.
    No crea notificación interna ni verifica preferencias.

    **Nota:** Los datos de ejemplo (emails, URLs de reseteo, códigos) son ficticios y solo con fines demostrativos.
    """
    user_email: str = Field(..., description="Email del usuario")
    user_name: str = Field(..., description="Nombre del usuario")
    reset_url: Optional[str] = Field(None, description="URL para resetear contraseña (ejemplo: 'https://campus360.com/reset-password/xyz789' - no es una URL real)")
    reset_code: Optional[str] = Field(None, description="Código de verificación numérico de 6 dígitos")

    # Metadatos opcionales
    source_module: Optional[str] = Field(None, description="Módulo de origen que genera el evento (ejemplo: 'AUTH', 'USER_MANAGEMENT', 'SECURITY')")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "user_email": "carlos.lopez@ejemplo.com",
                    "user_name": "Carlos López",
                    "reset_url": "https://campus360.com/reset-password/xyz789abc123",
                    "reset_code": "123456",
                    "source_module": "AUTH"
                }
            ]
        }
    }


class ComprobantePagoEventRequest(BaseModel):
    """
    Request para evento de comprobante de pago.

    Solo envía email de confirmación de pago al usuario.
    No crea notificación interna ni verifica preferencias.

    **Nota:** Los datos de ejemplo (emails, URLs, teléfonos) son ficticios y solo con fines demostrativos.
    """
    user_email: str = Field(..., description="Email del usuario")
    user_name: str = Field(..., description="Nombre del usuario")
    enlace: Optional[str] = Field(None, description="URL para ver detalles del comprobante (ejemplo: 'https://campus360.com/pagos/comprobante/abc123' - no es una URL real)")
    telefono: Optional[str] = Field(None, description="Teléfono de contacto para consultas sobre el pago")

    # Metadatos opcionales
    source_module: Optional[str] = Field(None, description="Módulo de origen que genera el evento (ejemplo: 'PAGOS', 'TESORERIA', 'FINANZAS')")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "user_email": "estudiante@ejemplo.com",
                    "user_name": "María López",
                    "enlace": "https://campus360.com/pagos/comprobante/abc123def456",
                    "telefono": "+51999888777",
                    "source_module": "PAGOS"
                }
            ]
        }
    }


class EventNotificationResponse(BaseModel):
    """
    Response unificada para todos los eventos
    """
    success: bool
    message: str
    internal_notification_id: Optional[int] = None
    channels_sent: list[str] = []  # ["email", "sms", "whatsapp"]
