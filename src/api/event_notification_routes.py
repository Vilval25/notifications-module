"""
Rutas de la API para eventos unificados de notificación
"""
from fastapi import FastAPI, HTTPException, status
from src.api.event_notification_models import (
    TramiteEventRequest,
    CreacionCuentaEventRequest,
    CambioContrasenaEventRequest,
    ComprobantePagoEventRequest,
    EventNotificationResponse
)
from src.business.event_notification_service import EventNotificationService


def register_event_notification_routes(app: FastAPI, event_notification_service: EventNotificationService):
    """
    Registra las rutas de eventos de notificación
    """

    @app.post(
        "/api/events/tramite",
        response_model=EventNotificationResponse,
        status_code=status.HTTP_200_OK,
        tags=["Módulos Externos"],
        summary="Procesar evento de trámite",
        description="""
        **Endpoint principal para módulos de trámites externos**

        Este endpoint procesa automáticamente eventos relacionados con trámites y solicitudes del sistema.
        Es el punto de integración para notificar al usuario sobre cambios en el estado de sus trámites.

        ## ¿Qué hace este endpoint?

        1. **Crea una notificación interna** que aparecerá en el panel del usuario
        2. **Consulta las preferencias** del usuario para notificaciones externas
        3. **Envía notificaciones** por los canales habilitados (email, SMS, WhatsApp)

        ## Eventos soportados

        - `tramite_registrado` - Se registró un nuevo trámite
        - `tramite_observado` - El trámite tiene observaciones que corregir
        - `tramite_aprobado` - El trámite fue aprobado exitosamente
        - `tramite_rechazado` - El trámite fue rechazado

        **Nota:** Consulta el schema del request para ver el formato exacto de los datos y usa el botón "Try it out" para probar con datos de ejemplo.
        """
    )
    async def process_tramite_event(request: TramiteEventRequest):
        """
        Procesa un evento de trámite
        """
        try:
            result = event_notification_service.process_tramite_event(
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

            return EventNotificationResponse(
                success=True,
                message=f"Evento procesado exitosamente. Notificación enviada por: {', '.join(result['channels_sent']) if result['channels_sent'] else 'ningún canal'}",
                internal_notification_id=result["internal_notification_id"],
                channels_sent=result["channels_sent"]
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error procesando evento de trámite: {str(e)}"
            )

    @app.post(
        "/api/events/creacion-cuenta",
        response_model=EventNotificationResponse,
        status_code=status.HTTP_200_OK,
        tags=["Módulos Externos"],
        summary="Procesar evento de creación de cuenta",
        description="""
        **Endpoint para módulos de gestión de usuarios**

        Este endpoint procesa la creación de nuevas cuentas de usuario enviando un email de bienvenida
        con instrucciones de activación o credenciales de acceso.

        ## ¿Qué hace este endpoint?

        Envía automáticamente un **email de bienvenida** al nuevo usuario con:
        - URL de activación de cuenta (si aplica)
        - Contraseña temporal generada (si aplica)
        - Instrucciones de primer acceso

        **Nota:** Consulta el schema del request para ver los campos disponibles y usa "Try it out" para probar.
        """
    )
    async def process_creacion_cuenta_event(request: CreacionCuentaEventRequest):
        """
        Procesa un evento de creación de cuenta
        """
        try:
            result = event_notification_service.process_creacion_cuenta_event(
                user_email=request.user_email,
                user_name=request.user_name,
                activation_url=request.activation_url,
                temporary_password=request.temporary_password,
                source_module=request.source_module
            )

            return EventNotificationResponse(
                success=True,
                message="Email de creación de cuenta enviado exitosamente",
                internal_notification_id=result["internal_notification_id"],
                channels_sent=result["channels_sent"]
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error procesando creación de cuenta: {str(e)}"
            )

    @app.post(
        "/api/events/cambio-contrasena",
        response_model=EventNotificationResponse,
        status_code=status.HTTP_200_OK,
        tags=["Módulos Externos"],
        summary="Procesar evento de cambio de contraseña",
        description="""
        **Endpoint para módulos de gestión de usuarios**

        Este endpoint procesa solicitudes de cambio o reseteo de contraseña enviando un email
        al usuario con las instrucciones y credenciales necesarias para completar el proceso.

        ## ¿Qué hace este endpoint?

        Envía automáticamente un **email de recuperación** con:
        - URL única para restablecer la contraseña (si aplica)
        - Código de verificación de 6 dígitos (si aplica)
        - Instrucciones paso a paso para el usuario

        **Nota:** Puedes enviar solo la URL, solo el código, o ambos según tu implementación. Consulta el schema para más detalles.
        """
    )
    async def process_cambio_contrasena_event(request: CambioContrasenaEventRequest):
        """
        Procesa un evento de cambio de contraseña
        """
        try:
            result = event_notification_service.process_cambio_contrasena_event(
                user_email=request.user_email,
                user_name=request.user_name,
                reset_url=request.reset_url,
                reset_code=request.reset_code,
                source_module=request.source_module
            )

            return EventNotificationResponse(
                success=True,
                message="Email de cambio de contraseña enviado exitosamente",
                internal_notification_id=result["internal_notification_id"],
                channels_sent=result["channels_sent"]
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error procesando cambio de contraseña: {str(e)}"
            )

    @app.post(
        "/api/events/comprobante-pago",
        response_model=EventNotificationResponse,
        status_code=status.HTTP_200_OK,
        tags=["Módulos Externos"],
        summary="Procesar evento de comprobante de pago",
        description="""
        **Endpoint para módulos de gestión de pagos**

        Este endpoint procesa la confirmación de pago enviando un email al usuario con
        el comprobante y detalles de su transacción.

        ## ¿Qué hace este endpoint?

        Envía automáticamente un **email de comprobante de pago** con:
        - Confirmación de pago recibido
        - Enlace para ver detalles del comprobante (si aplica)
        - Información de contacto para consultas

        **Nota:** Consulta el schema del request para ver los campos disponibles y usa "Try it out" para probar.
        """
    )
    async def process_comprobante_pago_event(request: ComprobantePagoEventRequest):
        """
        Procesa un evento de comprobante de pago
        """
        try:
            result = event_notification_service.process_comprobante_pago_event(
                user_email=request.user_email,
                user_name=request.user_name,
                enlace=request.enlace,
                telefono=request.telefono,
                source_module=request.source_module
            )

            return EventNotificationResponse(
                success=True,
                message="Email de comprobante de pago enviado exitosamente",
                internal_notification_id=result["internal_notification_id"],
                channels_sent=result["channels_sent"]
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error procesando comprobante de pago: {str(e)}"
            )
