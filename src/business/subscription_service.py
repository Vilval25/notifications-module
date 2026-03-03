"""
Servicio de negocio para gestionar suscripciones de notificaciones
"""
from typing import List, Dict
from src.domain.subscription import UserNotificationSubscription
from src.infrastructure.repository.sql_subscription_repository import SubscriptionRepository


class SubscriptionService:
    """
    Servicio de negocio para suscripciones de notificaciones
    """

    # Eventos de trámites disponibles
    TRAMITE_EVENTS = [
        "tramite_registrado",
        "tramite_observado",
        "tramite_aprobado",
        "tramite_rechazado"
    ]

    # Configuración por defecto: solo email habilitado para aprobado, rechazado y observado
    DEFAULT_SUBSCRIPTIONS = {
        "tramite_aprobado": {"email": True, "sms": False, "whatsapp": False},
        "tramite_rechazado": {"email": True, "sms": False, "whatsapp": False},
        "tramite_observado": {"email": True, "sms": False, "whatsapp": False},
        "tramite_registrado": {"email": False, "sms": False, "whatsapp": False}
    }

    def __init__(self, subscription_repository: SubscriptionRepository):
        self.subscription_repository = subscription_repository

    def get_user_subscriptions(self, user_id: str) -> List[UserNotificationSubscription]:
        """
        Obtiene todas las suscripciones de un usuario.
        Si el usuario no tiene suscripciones, las inicializa con valores por defecto.
        """
        subscriptions = self.subscription_repository.find_by_user(user_id)

        # Si no hay suscripciones, inicializar con valores por defecto
        if not subscriptions:
            subscriptions = self._initialize_default_subscriptions(user_id)

        return subscriptions

    def _initialize_default_subscriptions(self, user_id: str) -> List[UserNotificationSubscription]:
        """
        Inicializa las suscripciones por defecto para un usuario nuevo
        """
        subscriptions = []
        for event_type, config in self.DEFAULT_SUBSCRIPTIONS.items():
            subscription = UserNotificationSubscription(
                user_id=user_id,
                event_type=event_type,
                email_enabled=config["email"],
                sms_enabled=config["sms"],
                whatsapp_enabled=config["whatsapp"]
            )
            saved_subscription = self.subscription_repository.save(subscription)
            subscriptions.append(saved_subscription)

        return subscriptions

    def update_subscription(
        self,
        user_id: str,
        event_type: str,
        email_enabled: bool,
        sms_enabled: bool,
        whatsapp_enabled: bool
    ) -> UserNotificationSubscription:
        """
        Actualiza una suscripción de usuario
        """
        subscription = UserNotificationSubscription(
            user_id=user_id,
            event_type=event_type,
            email_enabled=email_enabled,
            sms_enabled=sms_enabled,
            whatsapp_enabled=whatsapp_enabled
        )

        return self.subscription_repository.save(subscription)

    def update_subscriptions_bulk(
        self,
        user_id: str,
        subscriptions_data: List[Dict]
    ) -> List[UserNotificationSubscription]:
        """
        Actualiza múltiples suscripciones de un usuario en una sola operación
        """
        updated_subscriptions = []

        for sub_data in subscriptions_data:
            subscription = self.update_subscription(
                user_id=user_id,
                event_type=sub_data["event_type"],
                email_enabled=sub_data.get("email_enabled", False),
                sms_enabled=sub_data.get("sms_enabled", False),
                whatsapp_enabled=sub_data.get("whatsapp_enabled", False)
            )
            updated_subscriptions.append(subscription)

        return updated_subscriptions

    def is_channel_enabled(self, user_id: str, event_type: str, channel: str) -> bool:
        """
        Verifica si un canal específico está habilitado para un usuario y evento

        Args:
            user_id: ID del usuario
            event_type: Tipo de evento
            channel: Canal de notificación ('email', 'sms', 'whatsapp')

        Returns:
            True si el canal está habilitado, False en caso contrario
        """
        subscription = self.subscription_repository.find_by_user_and_event(user_id, event_type)

        # Si no hay suscripción, usar valores por defecto
        if not subscription:
            defaults = self.DEFAULT_SUBSCRIPTIONS.get(event_type, {})
            return defaults.get(channel, False)

        # Retornar estado del canal
        if channel == "email":
            return subscription.email_enabled
        elif channel == "sms":
            return subscription.sms_enabled
        elif channel == "whatsapp":
            return subscription.whatsapp_enabled

        return False

    def get_enabled_channels(self, user_id: str, event_type: str) -> List[str]:
        """
        Obtiene la lista de canales habilitados para un usuario y evento

        Returns:
            Lista con los nombres de los canales habilitados: ['email', 'sms', 'whatsapp']
        """
        enabled_channels = []

        if self.is_channel_enabled(user_id, event_type, "email"):
            enabled_channels.append("email")
        if self.is_channel_enabled(user_id, event_type, "sms"):
            enabled_channels.append("sms")
        if self.is_channel_enabled(user_id, event_type, "whatsapp"):
            enabled_channels.append("whatsapp")

        return enabled_channels
