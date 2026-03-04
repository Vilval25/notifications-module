"""
Rutas de la API para eventos unificados de notificación
"""
from fastapi import FastAPI, HTTPException, status, BackgroundTasks
import logging
from src.api.event_notification_models import (
    TramiteEventRequest,
    CreacionCuentaEventRequest,
    CambioContrasenaEventRequest,
    ComprobantePagoEventRequest,
    EventNotificationResponse
)
from src.business.event_notification_service import EventNotificationService, TramiteEventData

# Configurar logger
logger = logging.getLogger(__name__)


def register_event_notification_routes(app: FastAPI, event_notification_service: EventNotificationService):
    """
    Registra las rutas de eventos de notificación
    """

    @app.post(
        "/api/events/tramite",
        response_model=EventNotificationResponse,
        status_code=status.HTTP_202_ACCEPTED,
        tags=["Módulos Externos"],
        summary="Procesar evento de trámite",
        description="""
        **Endpoint principal para módulos de trámites externos**

        Este endpoint **acepta y valida** eventos de trámites, procesándolos de forma asíncrona en segundo plano.
        Retorna respuesta inmediata después de validar los datos.

        ## ¿Qué hace este endpoint?

        1. **Valida los datos** del evento inmediatamente
        2. **Retorna respuesta 202 Accepted** (procesamiento en background)
        3. **Procesa en segundo plano**:
           - Crea notificación interna
           - Consulta preferencias del usuario
           - Envía notificaciones por canales habilitados

        ## Eventos soportados

        - `tramite_registrado` - Se registró un nuevo trámite
        - `tramite_observado` - El trámite tiene observaciones que corregir
        - `tramite_aprobado` - El trámite fue aprobado exitosamente
        - `tramite_rechazado` - El trámite fue rechazado

        ## Códigos de respuesta

        - **202 Accepted**: Evento aceptado y será procesado en background
        - **422 Unprocessable Entity**: Error de validación en los datos

        **Nota:** El procesamiento ocurre en segundo plano. La respuesta 202 indica que el evento fue aceptado, no que ya se completó el envío.
        """
    )
    async def process_tramite_event(request: TramiteEventRequest, background_tasks: BackgroundTasks):
        """
        Procesa un evento de trámite de forma asíncrona
        """
        # Validación adicional de event_type
        valid_event_types = ["tramite_registrado", "tramite_observado", "tramite_aprobado", "tramite_rechazado"]
        if request.event_type not in valid_event_types:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Tipo de evento inválido. Valores permitidos: {', '.join(valid_event_types)}"
            )

        # Validar email básico
        if not request.user_email or "@" not in request.user_email:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Email inválido. Se requiere un email válido."
            )

        # Crear DTO con los datos del evento
        event_data = TramiteEventData(
            user_id=request.user_id,
            user_email=request.user_email,
            user_name=request.user_name,
            user_phone=request.user_phone or "",
            solicitud_id=request.solicitud_id,
            event_type=request.event_type,
            solicitud_subject=request.solicitud_subject,
            solicitud_url=request.solicitud_url,
            source_module=request.source_module
        )

        # Encolar procesamiento en background
        background_tasks.add_task(
            event_notification_service.process_tramite_event,
            event_data
        )

        logger.info(f"Evento de trámite aceptado: {request.event_type} para usuario {request.user_id}")

        return EventNotificationResponse(
            status="accepted",
            message=f"Evento de trámite '{request.event_type}' aceptado. Se procesará en segundo plano."
        )

    @app.post(
        "/api/events/creacion-cuenta",
        response_model=EventNotificationResponse,
        status_code=status.HTTP_202_ACCEPTED,
        tags=["Módulos Externos"],
        summary="Procesar evento de creación de cuenta",
        description="""
        **Endpoint para módulos de gestión de usuarios**

        Acepta y valida eventos de creación de cuenta, procesándolos de forma asíncrona.

        ## ¿Qué hace este endpoint?

        1. **Valida los datos** del evento inmediatamente
        2. **Retorna respuesta 202 Accepted**
        3. **Procesa en segundo plano**: Envía email de bienvenida con URL de activación o contraseña temporal

        ## Códigos de respuesta

        - **202 Accepted**: Evento aceptado y será procesado en background
        - **422 Unprocessable Entity**: Error de validación

        **Nota:** El email se enviará en segundo plano después de aceptar el evento.
        """
    )
    async def process_creacion_cuenta_event(request: CreacionCuentaEventRequest, background_tasks: BackgroundTasks):
        """
        Procesa un evento de creación de cuenta de forma asíncrona
        """
        # Validar email
        if not request.user_email or "@" not in request.user_email:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Email inválido. Se requiere un email válido."
            )

        # Encolar procesamiento en background
        background_tasks.add_task(
            event_notification_service.process_creacion_cuenta_event,
            user_email=request.user_email,
            user_name=request.user_name,
            activation_url=request.activation_url,
            temporary_password=request.temporary_password,
            source_module=request.source_module
        )

        logger.info(f"Evento de creación de cuenta aceptado para email: {request.user_email}")

        return EventNotificationResponse(
            status="accepted",
            message="Evento de creación de cuenta aceptado. Email de bienvenida se enviará en segundo plano."
        )

    @app.post(
        "/api/events/cambio-contrasena",
        response_model=EventNotificationResponse,
        status_code=status.HTTP_202_ACCEPTED,
        tags=["Módulos Externos"],
        summary="Procesar evento de cambio de contraseña",
        description="""
        **Endpoint para módulos de gestión de usuarios**

        Acepta y valida eventos de cambio/reseteo de contraseña, procesándolos de forma asíncrona.

        ## ¿Qué hace este endpoint?

        1. **Valida los datos** del evento inmediatamente
        2. **Retorna respuesta 202 Accepted**
        3. **Procesa en segundo plano**: Envía email de recuperación con URL o código de reseteo

        ## Códigos de respuesta

        - **202 Accepted**: Evento aceptado y será procesado en background
        - **422 Unprocessable Entity**: Error de validación

        **Nota:** El email se enviará en segundo plano. Puedes enviar reset_url, reset_code o ambos.
        """
    )
    async def process_cambio_contrasena_event(request: CambioContrasenaEventRequest, background_tasks: BackgroundTasks):
        """
        Procesa un evento de cambio de contraseña de forma asíncrona
        """
        # Validar email
        if not request.user_email or "@" not in request.user_email:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Email inválido. Se requiere un email válido."
            )

        # Encolar procesamiento en background
        background_tasks.add_task(
            event_notification_service.process_cambio_contrasena_event,
            user_email=request.user_email,
            user_name=request.user_name,
            reset_url=request.reset_url,
            reset_code=request.reset_code,
            source_module=request.source_module
        )

        logger.info(f"Evento de cambio de contraseña aceptado para email: {request.user_email}")

        return EventNotificationResponse(
            status="accepted",
            message="Evento de cambio de contraseña aceptado. Email de recuperación se enviará en segundo plano."
        )

    @app.post(
        "/api/events/comprobante-pago",
        response_model=EventNotificationResponse,
        status_code=status.HTTP_202_ACCEPTED,
        tags=["Módulos Externos"],
        summary="Procesar evento de comprobante de pago",
        description="""
        **Endpoint para módulos de gestión de pagos**

        Acepta y valida eventos de comprobante de pago, procesándolos de forma asíncrona.

        ## ¿Qué hace este endpoint?

        1. **Valida los datos** del evento inmediatamente
        2. **Retorna respuesta 202 Accepted**
        3. **Procesa en segundo plano**: Envía email con comprobante de pago

        ## Códigos de respuesta

        - **202 Accepted**: Evento aceptado y será procesado en background
        - **422 Unprocessable Entity**: Error de validación

        **Nota:** El email con el comprobante se enviará en segundo plano.
        """
    )
    async def process_comprobante_pago_event(request: ComprobantePagoEventRequest, background_tasks: BackgroundTasks):
        """
        Procesa un evento de comprobante de pago de forma asíncrona
        """
        # Validar email
        if not request.user_email or "@" not in request.user_email:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Email inválido. Se requiere un email válido."
            )

        # Encolar procesamiento en background
        background_tasks.add_task(
            event_notification_service.process_comprobante_pago_event,
            user_email=request.user_email,
            user_name=request.user_name,
            enlace=request.enlace,
            telefono=request.telefono,
            source_module=request.source_module
        )

        logger.info(f"Evento de comprobante de pago aceptado para email: {request.user_email}")

        return EventNotificationResponse(
            status="accepted",
            message="Evento de comprobante de pago aceptado. Email se enviará en segundo plano."
        )
