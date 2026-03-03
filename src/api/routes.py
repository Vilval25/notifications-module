"""
API REST para el módulo de notificaciones usando FastAPI
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import Optional
from .models import (
    NotificationLogsResponse,
    NotificationLogResponse,
    HealthResponse,
    APIInfoResponse,
    ErrorResponse
)
from .template_models import (
    TemplateListResponse,
    TemplateDetailResponse,
    TemplateCreateRequest,
    TemplateUpdateRequest,
    TemplatePreviewRequest,
    TemplatePreviewResponse,
    TemplateValidationResponse,
    TemplateDeleteResponse,
    # Nuevos modelos
    EventType,
    TemplateWithStatusResponse,
    TemplateListWithStatusResponse,
    TemplateCreateRequestNew,
    TemplateUpdateRequestNew,
    TemplateDetailResponseNew,
    EventResponse,
    EventListResponse,
    ActivateEventRequest
)
from ..interface.notification_controller import NotificationController
from ..business.template_service import TemplateService


def create_app(notification_controller: NotificationController,
               template_service: TemplateService,
               event_repository) -> FastAPI:
    """
    Crea y configura la aplicación FastAPI

    Args:
        notification_controller: Controlador de notificaciones configurado
        template_service: Servicio de templates configurado
        event_repository: Repositorio de eventos de plantillas

    Returns:
        Aplicación FastAPI configurada con OpenAPI
    """
    app = FastAPI(
        title="API de Notificaciones",
        description="""
API REST para el módulo de notificaciones multi-canal de Campus360.

## Características

* **Multi-canal**: Envío por Email, SMS y WhatsApp
* **Sistema de Eventos**: Notificaciones basadas en eventos de negocio
* **Notificaciones Internas**: Panel de notificaciones para usuarios
* **Sistema de Suscripciones**: Preferencias de notificación por usuario y evento
* **Gestión de Plantillas**: CRUD completo con plantillas Handlebars activas por evento
* **Logging**: Registro completo de todas las notificaciones
* **Validación**: Validación automática con Pydantic

## Canales Disponibles

* `email` - Envío por correo electrónico (SMTP real)
* `sms` - Envío por SMS (Mock - simulado en consola)
* `whatsapp` - Envío por WhatsApp (Mock - simulado en consola)

## Eventos del Sistema

### Eventos de Trámites
* `tramite_registrado` - Nuevo trámite registrado
* `tramite_observado` - Trámite con observaciones
* `tramite_aprobado` - Trámite aprobado
* `tramite_rechazado` - Trámite rechazado

### Eventos de Cuenta
* `creacion_cuenta` - Creación de cuenta de usuario
* `cambio_contrasena` - Cambio o reseteo de contraseña

## Integración para Módulos Externos

Los módulos externos deben usar únicamente los 3 endpoints de eventos:
1. **POST /api/events/tramite** - Para eventos de trámites
2. **POST /api/events/creacion-cuenta** - Para creación de cuentas
3. **POST /api/events/cambio-contrasena** - Para cambio de contraseña

Cada endpoint procesa automáticamente:
- Crea notificación interna (panel del usuario)
- Verifica preferencias del usuario
- Envía notificaciones por canales habilitados
        """,
        version="2.0.0",
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
        description="Endpoint raíz con información general y links a documentación"
    )
    async def home():
        """
        Punto de entrada de la API con información general.

        **Para probar la API visita:** [/docs](/docs)

        ## Endpoints para Módulos Externos

        Los módulos externos solo deben usar estos 3 endpoints:
        - POST /api/events/tramite
        - POST /api/events/creacion-cuenta
        - POST /api/events/cambio-contrasena
        """
        return {
            "message": "API de Notificaciones - Campus360",
            "version": "2.0",
            "documentation": {
                "swagger": "/docs",
                "redoc": "/redoc",
                "openapi": "/openapi.json"
            },
            "endpoints_modulos_externos": {
                "POST /api/events/tramite": "Procesar eventos de trámites (registrado, observado, aprobado, rechazado)",
                "POST /api/events/creacion-cuenta": "Procesar creación de cuenta con email de bienvenida",
                "POST /api/events/cambio-contrasena": "Procesar cambio/reseteo de contraseña",
                "GET /api/notifications/logs": "Ver logs de notificaciones enviadas"
            },
            "otros_endpoints": {
                "GET /health": "Health check",
                "GET /api/events": "Listar eventos con plantillas activas",
                "GET /api/templates": "Gestión de plantillas (CRUD)",
                "GET /api/internal-notifications": "Notificaciones internas del usuario",
                "GET /api/subscriptions": "Preferencias de notificación del usuario"
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
        tags=["Módulos Externos"],
        summary="Obtener logs de notificaciones enviadas"
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
        response_model=TemplateListWithStatusResponse,
        tags=["Templates"],
        summary="Listar plantillas con estado",
        description="Obtiene la lista de todas las plantillas con metadata y estado activo/inactivo"
    )
    async def list_templates():
        """
        Lista todas las plantillas .hbs disponibles con su información completa.

        Incluye: nombre, asunto, evento asignado, estado (activa/inactiva), fecha de modificación
        """
        try:
            templates = template_service.list_templates_with_status()
            return {
                "templates": templates,
                "total": len(templates)
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get(
        "/api/templates/{name}",
        response_model=TemplateDetailResponseNew,
        tags=["Templates"],
        summary="Obtener plantilla",
        description="Obtiene el contenido y metadatos completos de una plantilla específica"
    )
    async def get_template(name: str):
        """
        Obtiene una plantilla por su nombre.

        **Args:**
        - name: Nombre de la plantilla sin extensión .hbs

        **Returns:**
        - Contenido de la plantilla, asunto, evento, estado y metadatos
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
        response_model=TemplateDetailResponseNew,
        status_code=201,
        tags=["Templates"],
        summary="Crear plantilla",
        description="Crea una nueva plantilla Handlebars con asunto y evento"
    )
    async def create_template(request: TemplateCreateRequestNew):
        """
        Crea una nueva plantilla con metadata.

        **Validaciones:**
        - El nombre no puede contener caracteres especiales
        - La sintaxis Handlebars debe ser válida
        - No puede existir otra plantilla con el mismo nombre
        - El evento debe ser uno de los 5 tipos válidos

        **Example:**
        ```json
        {
          "name": "tramite_aprobado_notif",
          "subject": "Tu trámite ha sido aprobado",
          "event_type": "tramite_aprobado",
          "content": "<h1>¡Hola {{nombre}}!</h1>\\n<p>Tu trámite ha sido aprobado.</p>"
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

            # Crear plantilla con subject y event_type
            success = template_service.create_template(
                request.name,
                request.content,
                request.subject,
                request.event_type.value
            )
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
        response_model=TemplateDetailResponseNew,
        tags=["Templates"],
        summary="Actualizar plantilla",
        description="Actualiza el asunto y contenido de una plantilla existente"
    )
    async def update_template(name: str, request: TemplateUpdateRequestNew):
        """
        Actualiza una plantilla existente.

        **Args:**
        - name: Nombre de la plantilla a actualizar
        - subject: Nuevo asunto del email
        - content: Nuevo contenido Handlebars
        - event_type: Nuevo tipo de evento (opcional, solo si no está activa)

        **Validaciones:**
        - La plantilla debe existir
        - La sintaxis Handlebars debe ser válida
        - Si se cambia el evento, la plantilla no debe estar activa

        **Nota:** El evento solo se puede cambiar si la plantilla NO está en uso.
        """
        try:
            # Validar sintaxis
            validation = template_service.validate_syntax(request.content)
            if not validation['valid']:
                raise HTTPException(
                    status_code=400,
                    detail=f"Sintaxis inválida: {validation['error']}"
                )

            # Si se está renombrando, hacerlo primero
            final_name = name
            if request.new_name and request.new_name != name:
                success = template_service.rename_template(name, request.new_name)
                if not success:
                    raise HTTPException(
                        status_code=404,
                        detail=f"No se pudo renombrar la plantilla '{name}'"
                    )
                final_name = request.new_name

            # Actualizar plantilla con subject y event_type opcional
            success = template_service.update_template(
                final_name,
                request.content,
                request.subject,
                request.event_type
            )
            if not success:
                raise HTTPException(
                    status_code=404,
                    detail=f"Plantilla '{final_name}' no encontrada"
                )

            # Retornar la plantilla actualizada
            template = template_service.get_template(final_name)
            return template
        except ValueError as ve:
            raise HTTPException(status_code=400, detail=str(ve))
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.delete(
        "/api/templates/{name}",
        response_model=TemplateDeleteResponse,
        tags=["Templates"],
        summary="Eliminar plantilla",
        description="Elimina una plantilla del sistema si no está activa"
    )
    async def delete_template(name: str):
        """
        Elimina una plantilla.

        **Args:**
        - name: Nombre de la plantilla a eliminar

        **Validaciones:**
        - No se puede eliminar una plantilla que está activa (en uso)
        - Primero debe activarse otra plantilla para el evento

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
        except ValueError as e:
            # Error de validación (plantilla activa)
            raise HTTPException(status_code=400, detail=str(e))
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # ============================================
    # ENDPOINTS DE GESTIÓN DE EVENTOS
    # ============================================

    @app.get(
        "/api/events",
        response_model=EventListResponse,
        tags=["Events"],
        summary="Listar eventos",
        description="Obtiene todos los eventos del sistema con sus plantillas activas"
    )
    async def list_events():
        """
        Lista todos los eventos con sus plantillas activas asignadas.

        Los eventos son fijos en el sistema:
        - tramite_observado
        - tramite_aprobado
        - tramite_rechazado
        - confirmacion_cambio_password
        - comprobante_pago
        """
        try:
            events_data = event_repository.get_all_events()
            events = []

            for event in events_data:
                events.append({
                    "event_type": event.event_type,
                    "template_name": event.template_name,
                    "is_active": event.is_active
                })

            return {
                "events": events,
                "total": len(events)
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.put(
        "/api/events/{event_type}/activate",
        response_model=EventResponse,
        tags=["Events"],
        summary="Activar plantilla para evento",
        description="Activa una plantilla para un evento específico (desactiva la anterior)"
    )
    async def activate_template_for_event(event_type: str, request: ActivateEventRequest):
        """
        Activa una plantilla para un evento.

        **Args:**
        - event_type: Tipo de evento (tramite_observado, tramite_aprobado, etc.)
        - template_name: Nombre de la plantilla a activar

        **Comportamiento:**
        - La plantilla anterior para este evento se desactiva automáticamente
        - Solo puede haber UNA plantilla activa por evento

        **Example:**
        ```json
        {
          "template_name": "bienvenida"
        }
        ```
        """
        try:
            # Validar que el evento exista
            event = event_repository.get_event_by_type(event_type)
            if not event:
                raise HTTPException(
                    status_code=404,
                    detail=f"Evento '{event_type}' no encontrado"
                )

            # Validar que la plantilla exista
            template = template_service.get_template(request.template_name)
            if not template:
                raise HTTPException(
                    status_code=404,
                    detail=f"Plantilla '{request.template_name}' no encontrada"
                )

            # Activar plantilla para el evento
            success = event_repository.activate_template_for_event(
                event_type,
                request.template_name
            )

            if not success:
                raise HTTPException(
                    status_code=500,
                    detail="Error activando plantilla para el evento"
                )

            # Retornar evento actualizado
            updated_event = event_repository.get_event_by_type(event_type)
            return {
                "event_type": updated_event.event_type,
                "template_name": updated_event.template_name,
                "is_active": updated_event.is_active
            }

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # ============================================
    # ENDPOINTS DE PREVIEW Y VALIDACIÓN
    # ============================================

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

    # ============================================
    # ENDPOINTS DE NOTIFICACIONES INTERNAS
    # ============================================
    # Nota: Los endpoints de notificaciones internas se configuran
    # en create_internal_notifications_app() y se registran por separado

    return app
