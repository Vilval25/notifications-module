"""
Modelos Pydantic para la API de suscripciones
"""
from pydantic import BaseModel, Field
from typing import List
from datetime import datetime


class SubscriptionUpdateRequest(BaseModel):
    """Modelo para actualizar una suscripción individual"""
    event_type: str = Field(..., description="Tipo de evento")
    email_enabled: bool = Field(False, description="Notificación por email habilitada")
    sms_enabled: bool = Field(False, description="Notificación por SMS habilitada")
    whatsapp_enabled: bool = Field(False, description="Notificación por WhatsApp habilitada")


class SubscriptionBulkUpdateRequest(BaseModel):
    """Modelo para actualizar múltiples suscripciones"""
    subscriptions: List[SubscriptionUpdateRequest] = Field(..., description="Lista de suscripciones a actualizar")


class SubscriptionResponse(BaseModel):
    """Modelo de respuesta para una suscripción"""
    id: int
    user_id: str
    event_type: str
    email_enabled: bool
    sms_enabled: bool
    whatsapp_enabled: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SubscriptionListResponse(BaseModel):
    """Modelo de respuesta para lista de suscripciones"""
    subscriptions: List[SubscriptionResponse]
    total: int
