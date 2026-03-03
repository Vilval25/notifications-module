"""
Rutas de la API para gestión de suscripciones de notificaciones
"""
from fastapi import FastAPI, HTTPException
from src.api.subscription_models import (
    SubscriptionUpdateRequest,
    SubscriptionBulkUpdateRequest,
    SubscriptionResponse,
    SubscriptionListResponse
)
from src.business.subscription_service import SubscriptionService


def register_subscription_routes(app: FastAPI, subscription_service: SubscriptionService):
    """
    Registra las rutas de suscripciones en la aplicación FastAPI
    """

    @app.get(
        "/api/subscriptions/user/{user_id}",
        response_model=SubscriptionListResponse,
        tags=["Subscriptions"],
        summary="Obtener suscripciones de usuario",
        description="Obtiene todas las suscripciones de notificaciones de un usuario. Si no existen, las inicializa con valores por defecto."
    )
    async def get_user_subscriptions(user_id: str):
        """
        Obtiene las suscripciones de un usuario
        """
        try:
            subscriptions = subscription_service.get_user_subscriptions(user_id)

            return SubscriptionListResponse(
                subscriptions=[
                    SubscriptionResponse(
                        id=sub.id,
                        user_id=sub.user_id,
                        event_type=sub.event_type,
                        email_enabled=sub.email_enabled,
                        sms_enabled=sub.sms_enabled,
                        whatsapp_enabled=sub.whatsapp_enabled,
                        created_at=sub.created_at,
                        updated_at=sub.updated_at
                    )
                    for sub in subscriptions
                ],
                total=len(subscriptions)
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.put(
        "/api/subscriptions/user/{user_id}",
        response_model=SubscriptionResponse,
        tags=["Subscriptions"],
        summary="Actualizar suscripción",
        description="Actualiza una suscripción individual de un usuario"
    )
    async def update_subscription(user_id: str, request: SubscriptionUpdateRequest):
        """
        Actualiza una suscripción de usuario
        """
        try:
            subscription = subscription_service.update_subscription(
                user_id=user_id,
                event_type=request.event_type,
                email_enabled=request.email_enabled,
                sms_enabled=request.sms_enabled,
                whatsapp_enabled=request.whatsapp_enabled
            )

            return SubscriptionResponse(
                id=subscription.id,
                user_id=subscription.user_id,
                event_type=subscription.event_type,
                email_enabled=subscription.email_enabled,
                sms_enabled=subscription.sms_enabled,
                whatsapp_enabled=subscription.whatsapp_enabled,
                created_at=subscription.created_at,
                updated_at=subscription.updated_at
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.put(
        "/api/subscriptions/user/{user_id}/bulk",
        response_model=SubscriptionListResponse,
        tags=["Subscriptions"],
        summary="Actualizar suscripciones en lote",
        description="Actualiza múltiples suscripciones de un usuario en una sola operación"
    )
    async def update_subscriptions_bulk(user_id: str, request: SubscriptionBulkUpdateRequest):
        """
        Actualiza múltiples suscripciones de un usuario
        """
        try:
            subscriptions_data = [
                {
                    "event_type": sub.event_type,
                    "email_enabled": sub.email_enabled,
                    "sms_enabled": sub.sms_enabled,
                    "whatsapp_enabled": sub.whatsapp_enabled
                }
                for sub in request.subscriptions
            ]

            updated_subscriptions = subscription_service.update_subscriptions_bulk(
                user_id=user_id,
                subscriptions_data=subscriptions_data
            )

            return SubscriptionListResponse(
                subscriptions=[
                    SubscriptionResponse(
                        id=sub.id,
                        user_id=sub.user_id,
                        event_type=sub.event_type,
                        email_enabled=sub.email_enabled,
                        sms_enabled=sub.sms_enabled,
                        whatsapp_enabled=sub.whatsapp_enabled,
                        created_at=sub.created_at,
                        updated_at=sub.updated_at
                    )
                    for sub in updated_subscriptions
                ],
                total=len(updated_subscriptions)
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get(
        "/api/subscriptions/user/{user_id}/event/{event_type}/channels",
        response_model=dict,
        tags=["Subscriptions"],
        summary="Obtener canales habilitados",
        description="Obtiene los canales de notificación habilitados para un usuario y evento específico"
    )
    async def get_enabled_channels(user_id: str, event_type: str):
        """
        Obtiene los canales habilitados para un usuario y evento
        """
        try:
            enabled_channels = subscription_service.get_enabled_channels(user_id, event_type)

            return {
                "user_id": user_id,
                "event_type": event_type,
                "enabled_channels": enabled_channels,
                "email": "email" in enabled_channels,
                "sms": "sms" in enabled_channels,
                "whatsapp": "whatsapp" in enabled_channels
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
