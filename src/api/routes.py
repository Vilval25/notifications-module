"""
API REST para el módulo de notificaciones usando FastAPI
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from .models import (
    NotificationSendRequest,
    NotificationSendResponse,
    NotificationLogsResponse,
    NotificationLogResponse,
    HealthResponse,
    APIInfoResponse,
    ErrorResponse,
    ChannelEnum
)
from ..domain.notification_channel import NotificationChannel
from ..interface.notification_request import NotificationRequest
from ..interface.notification_controller import NotificationController


def create_app(notification_controller: NotificationController) -> FastAPI:
    """
    Crea y configura la aplicación FastAPI

    Args:
        notification_controller: Controlador de notificaciones configurado

    Returns:
        Aplicación FastAPI configurada con OpenAPI
    """
    app = FastAPI(
        title="API de Notificaciones",
        description="""
API REST para el módulo de notificaciones multi-canal de Campus360.

## Características

* **Multi-canal**: Envío por Email, SMS y WhatsApp
* **Plantillas**: Sistema de plantillas Handlebars
* **Logging**: Registro completo de todas las notificaciones
* **Validación**: Validación automática con Pydantic

## Canales Disponibles

* `email` - Envío por correo electrónico (SMTP)
* `sms` - Envío por SMS (Twilio)
* `whatsapp` - Envío por WhatsApp (Meta Business API)
        """,
        version="1.0.0",
        contact={
            "name": "Soporte Campus360",
            "email": "soporte@campus360.com"
        },
        license_info={
            "name": "MIT"
        }
    )

    # Configurar CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.get(
        "/",
        response_model=APIInfoResponse,
        tags=["Info"],
        summary="Información de la API",
        description="Endpoint raíz que redirige a la documentación interactiva"
    )
    async def home():
        """
        Punto de entrada de la API con links a la documentación.

        **Para probar la API visita:** [/docs](/docs)
        """
        return {
            "message": "API de Notificaciones - Campus360",
            "version": "1.0",
            "documentation": {
                "swagger": "/docs",
                "redoc": "/redoc",
                "openapi": "/openapi.json"
            },
            "endpoints": {
                "GET /health": "Health check",
                "POST /api/notifications/send": "Enviar notificación",
                "GET /api/notifications/logs": "Ver logs"
            }
        }

    @app.get(
        "/health",
        response_model=HealthResponse,
        tags=["Health"],
        summary="Verificar estado del servicio"
    )
    async def health():
        """
        Endpoint de health check para verificar que el servicio está funcionando
        """
        return {"status": "healthy"}

    @app.post(
        "/api/notifications/send",
        response_model=NotificationSendResponse,
        responses={
            200: {
                "description": "Notificación enviada exitosamente",
                "model": NotificationSendResponse
            },
            400: {
                "description": "Datos inválidos en la solicitud",
                "model": ErrorResponse
            },
            500: {
                "description": "Error interno del servidor",
                "model": ErrorResponse
            }
        },
        tags=["Notifications"],
        summary="Enviar notificación"
    )
    async def send_notification(request: NotificationSendRequest):
        """
        Envía una notificación a través del canal especificado.

        ## Parámetros

        * **recipient**: Destinatario (email, teléfono, etc.)
        * **channel**: Canal de envío (email, sms, whatsapp)
        * **template_name**: Nombre de la plantilla a usar
        * **params**: Parámetros para renderizar la plantilla

        ## Ejemplo

        ```json
        {
          "recipient": "usuario@ejemplo.com",
          "channel": "email",
          "template_name": "welcome",
          "params": {
            "name": "Juan Pérez",
            "source_module": "USER_REGISTRATION"
          }
        }
        ```

        ## Respuesta Exitosa

        ```json
        {
          "status": "success",
          "message": "Notificación enviada correctamente"
        }
        ```
        """
        try:
            # Mapear canal de string a enum del dominio
            channel_map = {
                ChannelEnum.EMAIL: NotificationChannel.EMAIL,
                ChannelEnum.SMS: NotificationChannel.SMS,
                ChannelEnum.WHATSAPP: NotificationChannel.WHATSAPP
            }

            channel = channel_map[request.channel]

            # Crear request del dominio
            notification_request = NotificationRequest(
                recipient=request.recipient,
                channel=channel,
                template_name=request.template_name,
                params=request.params
            )

            # Enviar notificación
            result = notification_controller.send_notification(notification_request)

            if result['status'] == 'success':
                return result
            else:
                raise HTTPException(status_code=500, detail=result.get('message', 'Error al enviar notificación'))

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get(
        "/api/notifications/logs",
        response_model=NotificationLogsResponse,
        responses={
            200: {
                "description": "Lista de logs obtenida exitosamente",
                "model": NotificationLogsResponse
            },
            500: {
                "description": "Error interno del servidor",
                "model": ErrorResponse
            }
        },
        tags=["Notifications"],
        summary="Obtener logs de notificaciones"
    )
    async def get_logs(
        limit: Optional[int] = Query(
            None,
            description="Número máximo de logs a devolver",
            ge=1,
            le=1000,
            examples=[10]
        )
    ):
        """
        Obtiene los logs de notificaciones enviadas.

        ## Parámetros de Query

        * **limit** (opcional): Número máximo de logs a devolver (1-1000)

        ## Ejemplo

        GET /api/notifications/logs?limit=10

        ## Respuesta

        ```json
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
              "source_module": "USER_REGISTRATION"
            }
          ]
        }
        ```
        """
        try:
            logs = notification_controller.get_logs()

            # Convertir logs a modelos Pydantic
            logs_response = []
            for log in logs:
                logs_response.append(NotificationLogResponse(
                    id=log.id,
                    recipient=log.recipient,
                    channel=log.channel.value,
                    content=log.content[:100] + "..." if len(log.content) > 100 else log.content,
                    status=log.status,
                    timestamp=log.timestamp.isoformat(),
                    source_module=log.source_module
                ))

            # Aplicar límite si se especificó
            if limit:
                logs_response = logs_response[:limit]

            return {
                "total": len(logs_response),
                "logs": logs_response
            }

        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return app
