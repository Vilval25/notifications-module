"""
API REST para el módulo de notificaciones usando FastAPI
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
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
from .template_models import (
    TemplateListResponse,
    TemplateDetailResponse,
    TemplateCreateRequest,
    TemplateUpdateRequest,
    TemplatePreviewRequest,
    TemplatePreviewResponse,
    TemplateValidationResponse,
    TemplateDeleteResponse
)
from ..domain.notification_channel import NotificationChannel
from ..interface.notification_request import NotificationRequest
from ..interface.notification_controller import NotificationController
from ..business.template_service import TemplateService


def create_app(notification_controller: NotificationController, template_service: TemplateService) -> FastAPI:
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
          "template_name": "bienvenida",
          "params": {
            "name": "Fabián García",
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

    # ============================================
    # ENDPOINTS DE GESTIÓN DE PLANTILLAS
    # ============================================

    # Montar archivos estáticos
    app.mount("/static", StaticFiles(directory="static"), name="static")

    @app.get(
        "/templates-ui",
        tags=["Templates UI"],
        summary="Interfaz web de gestión de plantillas",
        include_in_schema=False
    )
    async def templates_ui():
        """Sirve la interfaz web de gestión de plantillas"""
        return FileResponse("static/index.html")

    @app.get(
        "/api/templates",
        response_model=TemplateListResponse,
        tags=["Templates"],
        summary="Listar plantillas",
        description="Obtiene la lista de todas las plantillas Handlebars disponibles"
    )
    async def list_templates():
        """
        Lista todas las plantillas .hbs disponibles en el sistema.

        Retorna los nombres sin la extensión .hbs
        """
        try:
            templates = template_service.list_templates()
            return {
                "templates": templates,
                "total": len(templates)
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get(
        "/api/templates/{name}",
        response_model=TemplateDetailResponse,
        tags=["Templates"],
        summary="Obtener plantilla",
        description="Obtiene el contenido y metadatos de una plantilla específica"
    )
    async def get_template(name: str):
        """
        Obtiene una plantilla por su nombre.

        **Args:**
        - name: Nombre de la plantilla sin extensión .hbs

        **Returns:**
        - Contenido de la plantilla y metadatos
        """
        try:
            template = template_service.get_template(name)
            if template is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"Plantilla '{name}' no encontrada"
                )
            return template
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post(
        "/api/templates",
        response_model=TemplateDetailResponse,
        status_code=201,
        tags=["Templates"],
        summary="Crear plantilla",
        description="Crea una nueva plantilla Handlebars"
    )
    async def create_template(request: TemplateCreateRequest):
        """
        Crea una nueva plantilla.

        **Validaciones:**
        - El nombre no puede contener caracteres especiales
        - La sintaxis Handlebars debe ser válida
        - No puede existir otra plantilla con el mismo nombre

        **Example:**
        ```json
        {
          "name": "password_reset",
          "content": "<h1>Restablecer contraseña</h1>\\n<p>Hola {{name}}</p>"
        }
        ```
        """
        try:
            # Validar sintaxis
            validation = template_service.validate_syntax(request.content)
            if not validation['valid']:
                raise HTTPException(
                    status_code=400,
                    detail=f"Sintaxis inválida: {validation['error']}"
                )

            # Crear plantilla
            success = template_service.create_template(request.name, request.content)
            if not success:
                raise HTTPException(
                    status_code=409,
                    detail=f"La plantilla '{request.name}' ya existe"
                )

            # Retornar la plantilla creada
            template = template_service.get_template(request.name)
            return template
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.put(
        "/api/templates/{name}",
        response_model=TemplateDetailResponse,
        tags=["Templates"],
        summary="Actualizar plantilla",
        description="Actualiza el contenido de una plantilla existente"
    )
    async def update_template(name: str, request: TemplateUpdateRequest):
        """
        Actualiza una plantilla existente.

        **Args:**
        - name: Nombre de la plantilla a actualizar
        - content: Nuevo contenido Handlebars

        **Validaciones:**
        - La plantilla debe existir
        - La sintaxis Handlebars debe ser válida
        """
        try:
            # Validar sintaxis
            validation = template_service.validate_syntax(request.content)
            if not validation['valid']:
                raise HTTPException(
                    status_code=400,
                    detail=f"Sintaxis inválida: {validation['error']}"
                )

            # Actualizar plantilla
            success = template_service.update_template(name, request.content)
            if not success:
                raise HTTPException(
                    status_code=404,
                    detail=f"Plantilla '{name}' no encontrada"
                )

            # Retornar la plantilla actualizada
            template = template_service.get_template(name)
            return template
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.delete(
        "/api/templates/{name}",
        response_model=TemplateDeleteResponse,
        tags=["Templates"],
        summary="Eliminar plantilla",
        description="Elimina una plantilla del sistema"
    )
    async def delete_template(name: str):
        """
        Elimina una plantilla.

        **Args:**
        - name: Nombre de la plantilla a eliminar

        **Warning:** Esta operación es irreversible
        """
        try:
            success = template_service.delete_template(name)
            if not success:
                raise HTTPException(
                    status_code=404,
                    detail=f"Plantilla '{name}' no encontrada"
                )

            return {
                "status": "success",
                "message": f"Plantilla '{name}' eliminada correctamente"
            }
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post(
        "/api/templates/preview",
        response_model=TemplatePreviewResponse,
        tags=["Templates"],
        summary="Preview de plantilla",
        description="Renderiza una plantilla con datos de prueba sin guardarla"
    )
    async def preview_template(request: TemplatePreviewRequest):
        """
        Renderiza una plantilla con parámetros de prueba.

        Útil para ver el resultado antes de guardar la plantilla.

        **Example:**
        ```json
        {
          "content": "<h1>Hola {{name}}!</h1>",
          "params": {
            "name": "Juan Pérez"
          }
        }
        ```
        """
        try:
            result = template_service.preview_template(request.content, request.params)
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.post(
        "/api/templates/validate",
        response_model=TemplateValidationResponse,
        tags=["Templates"],
        summary="Validar sintaxis",
        description="Valida la sintaxis Handlebars sin guardar la plantilla"
    )
    async def validate_template(request: TemplatePreviewRequest):
        """
        Valida la sintaxis de una plantilla Handlebars.

        **Args:**
        - content: Contenido Handlebars a validar

        **Returns:**
        - valid: Si la sintaxis es correcta
        - error: Mensaje de error si hay problemas
        """
        try:
            result = template_service.validate_syntax(request.content)
            return result
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return app
