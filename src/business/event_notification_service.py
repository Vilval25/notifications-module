"""
Servicio orquestador de eventos de notificación
Maneja la lógica completa: notificación interna + verificar preferencias + enviar
"""
from typing import Dict, Any, List
from dataclasses import dataclass
from src.business.internal_notification_service import InternalNotificationService
from src.business.subscription_service import SubscriptionService
from src.interface.notification_controller import NotificationController
from src.interface.notification_request import NotificationRequest
from src.domain.notification_channel import NotificationChannel


@dataclass
class TramiteEventData:
    """DTO para datos de evento de trámite"""
    user_id: str
    user_email: str
    user_name: str
    user_phone: str
    solicitud_id: str
    event_type: str
    solicitud_subject: str
    solicitud_url: str
    source_module: str


class EventNotificationService:
    """
    Servicio que orquesta el flujo completo de notificaciones por eventos
    """

    def __init__(
        self,
        internal_notification_service: InternalNotificationService,
        subscription_service: SubscriptionService,
        notification_controller: NotificationController
    ):
        self.internal_notification_service = internal_notification_service
        self.subscription_service = subscription_service
        self.notification_controller = notification_controller

    def process_tramite_event(self, event_data: TramiteEventData) -> Dict[str, Any]:
        """
        Procesa un evento de trámite:
        1. Crea notificación interna (SIEMPRE)
        2. Verifica preferencias del usuario
        3. Envía notificaciones externas según canales habilitados

        Args:
            event_data: DTO con todos los datos del evento de trámite

        Returns:
            Dict con información del proceso:
            - internal_notification_id: ID de la notificación interna creada
            - channels_sent: Lista de canales por los que se envió
        """
        # 1. Crear notificación interna
        notification_subject = self._generate_notification_subject(event_data.event_type)
        internal_notification = self.internal_notification_service.create_notification_from_event({
            "user_id": event_data.user_id,
            "solicitud_id": event_data.solicitud_id,
            "event_type": event_data.event_type,
            "notification_subject": notification_subject,
            "solicitud_subject": event_data.solicitud_subject,
            "solicitud_url": event_data.solicitud_url
        })

        # 2. Verificar canales habilitados
        enabled_channels = self.subscription_service.get_enabled_channels(
            event_data.user_id,
            event_data.event_type
        )

        # 3. Preparar variables y enviar por cada canal
        variables = self._prepare_template_variables(event_data)
        channels_sent = self._send_notifications_to_channels(
            enabled_channels,
            event_data,
            variables
        )

        return {
            "internal_notification_id": internal_notification.id,
            "channels_sent": channels_sent
        }

    def process_creacion_cuenta_event(
        self,
        user_email: str,
        user_name: str,
        activation_url: str,
        temporary_password: str,
        source_module: str
    ) -> Dict[str, Any]:
        """
        Procesa evento de creación de cuenta
        Solo envía email (no hay notificación interna ni verificación de preferencias)
        """
        optional_vars = {
            "enlace": activation_url,
            "telefono": "",
            "source_module": source_module,
            "password": temporary_password
        }

        return self._send_email_notification(
            template_name="creacion_cuenta",
            user_email=user_email,
            user_name=user_name,
            optional_vars=optional_vars
        )

    def process_cambio_contrasena_event(
        self,
        user_email: str,
        user_name: str,
        reset_url: str,
        reset_code: str,
        source_module: str
    ) -> Dict[str, Any]:
        """
        Procesa evento de cambio/reseteo de contraseña
        Solo envía email (no hay notificación interna ni verificación de preferencias)
        """
        optional_vars = {
            "enlace": reset_url,
            "telefono": "",
            "source_module": source_module,
            "codigo": reset_code
        }

        return self._send_email_notification(
            template_name="cambio_contrasena",
            user_email=user_email,
            user_name=user_name,
            optional_vars=optional_vars
        )

    def process_comprobante_pago_event(
        self,
        user_email: str,
        user_name: str,
        enlace: str,
        telefono: str,
        source_module: str
    ) -> Dict[str, Any]:
        """
        Procesa evento de comprobante de pago
        Solo envía email (no hay notificación interna ni verificación de preferencias)
        """
        optional_vars = {
            "enlace": enlace,
            "telefono": telefono,
            "source_module": source_module
        }

        return self._send_email_notification(
            template_name="comprobante_pago",
            user_email=user_email,
            user_name=user_name,
            optional_vars=optional_vars
        )

    def _prepare_template_variables(self, event_data: TramiteEventData) -> Dict[str, Any]:
        """
        Prepara el diccionario de variables para las plantillas

        Args:
            event_data: DTO con los datos del evento de trámite

        Returns:
            Diccionario con las variables para la plantilla
        """
        return {
            "nombre": event_data.user_name,
            "email": event_data.user_email,
            "enlace": event_data.solicitud_url,
            "telefono": event_data.user_phone,
            "source_module": event_data.source_module
        }

    def _send_notifications_to_channels(
        self,
        enabled_channels: List[str],
        event_data: TramiteEventData,
        variables: Dict[str, Any]
    ) -> List[str]:
        """
        Envía notificaciones por cada canal habilitado

        Args:
            enabled_channels: Lista de nombres de canales habilitados
            event_data: DTO con los datos del evento de trámite
            variables: Variables para las plantillas

        Returns:
            Lista de nombres de canales por los que se envió exitosamente
        """
        channels_sent = []

        for channel_name in enabled_channels:
            try:
                # Mapear nombre de canal a enum
                channel = self._map_channel_name(channel_name)

                # Determinar destinatario según el canal
                to = self._get_recipient_for_channel(
                    channel_name,
                    event_data.user_email,
                    event_data.user_phone
                )

                if to:
                    # Crear request de notificación
                    notification_request = NotificationRequest(
                        recipient=to,
                        channel=channel,
                        template_name=event_data.event_type,
                        params=variables
                    )

                    # Enviar notificación
                    result = self.notification_controller.send_notification(notification_request)

                    if result["status"] == "success":
                        channels_sent.append(channel_name)
            except Exception as e:
                # Log error pero continuar con otros canales
                pass  # Silenciar errores para evitar problemas de codificación

        return channels_sent

    def _send_email_notification(
        self,
        template_name: str,
        user_email: str,
        user_name: str,
        optional_vars: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Método genérico para enviar notificaciones por email

        Args:
            template_name: Nombre de la plantilla a usar
            user_email: Email del destinatario
            user_name: Nombre del destinatario
            optional_vars: Variables adicionales para la plantilla (enlace, telefono, source_module, etc.)

        Returns:
            Dict con información del proceso:
            - internal_notification_id: None (no hay notificación interna)
            - channels_sent: Lista con "email" si fue exitoso, lista vacía si falló
        """
        # Construir variables base
        variables = {
            "nombre": user_name,
            "email": user_email
        }

        # Agregar variables opcionales
        variables.update(optional_vars)

        try:
            notification_request = NotificationRequest(
                recipient=user_email,
                channel=NotificationChannel.EMAIL,
                template_name=template_name,
                params=variables
            )

            result = self.notification_controller.send_notification(notification_request)

            return {
                "internal_notification_id": None,
                "channels_sent": ["email"] if result["status"] == "success" else []
            }
        except Exception as e:
            print(f"Error enviando email con plantilla '{template_name}': {e}")
            return {
                "internal_notification_id": None,
                "channels_sent": []
            }

    def _map_channel_name(self, channel_name: str) -> NotificationChannel:
        """Mapea nombre de canal a enum"""
        mapping = {
            "email": NotificationChannel.EMAIL,
            "sms": NotificationChannel.SMS,
            "whatsapp": NotificationChannel.WHATSAPP
        }
        return mapping.get(channel_name, NotificationChannel.EMAIL)

    def _get_recipient_for_channel(self, channel_name: str, email: str, phone: str) -> str:
        """Obtiene el destinatario correcto según el canal"""
        if channel_name == "email":
            return email
        elif channel_name in ["sms", "whatsapp"]:
            return phone
        return email

    def _generate_notification_subject(self, event_type: str) -> str:
        """
        Genera automáticamente el asunto de la notificación según el tipo de evento

        Args:
            event_type: Tipo de evento (tramite_registrado, tramite_observado, etc.)

        Returns:
            Asunto de la notificación
        """
        subjects = {
            "tramite_registrado": "Tu trámite ha sido registrado",
            "tramite_observado": "Tu trámite tiene observaciones",
            "tramite_aprobado": "Tu trámite ha sido aprobado",
            "tramite_rechazado": "Tu trámite ha sido rechazado"
        }
        return subjects.get(event_type, "Actualización de tu trámite")
