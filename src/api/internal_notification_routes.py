"""
API REST para notificaciones internas del sistema
"""

from fastapi import HTTPException, Query
from typing import Optional
from .internal_notification_models import (
    InternalNotificationCreateRequest,
    InternalNotificationResponse,
    InternalNotificationListResponse,
    MarkAsReadResponse,
    UnreadCountResponse,
    NotificationSummaryResponse
)
from ..business.internal_notification_service import InternalNotificationService


def register_internal_notification_routes(app, internal_notification_service: InternalNotificationService):
    """
    Registra las rutas de notificaciones internas en la aplicación FastAPI

    Args:
        app: Aplicación FastAPI
        internal_notification_service: Servicio de notificaciones internas configurado
    """

    @app.post(
        "/api/internal-notifications",
        response_model=InternalNotificationResponse,
        status_code=201,
        tags=["Internal Notifications"],
        summary="Crear notificación interna",
        description="Crea una nueva notificación interna para mostrar en el panel de usuario"
    )
    async def create_internal_notification(request: InternalNotificationCreateRequest):
        """
        Crea una notificación interna a partir de un evento de trámite.

        **Este endpoint es llamado automáticamente cuando ocurre un evento de trámite.**

        **Args:**
        - user_id: ID del usuario destinatario
        - solicitud_id: ID de la solicitud/trámite
        - event_type: Tipo de evento (tramite_registrado, tramite_aprobado, etc.)
        - notification_subject: Asunto de la notificación
        - solicitud_subject: Asunto de la solicitud
        - solicitud_url: URL para ir a la solicitud (opcional)

        **Example:**
        ```json
        {
          "user_id": "user123",
          "solicitud_id": "SOL-2024-001",
          "event_type": "tramite_aprobado",
          "notification_subject": "Trámite aprobado",
          "solicitud_subject": "Solicitud de certificado de estudios",
          "solicitud_url": "https://campus360.com/tramites/SOL-2024-001"
        }
        ```
        """
        try:
            notification = internal_notification_service.create_notification_from_event(
                request.model_dump()
            )

            return InternalNotificationResponse(
                id=notification.id,
                user_id=notification.user_id,
                solicitud_id=notification.solicitud_id,
                event_type=notification.event_type,
                notification_subject=notification.notification_subject,
                solicitud_subject=notification.solicitud_subject,
                is_read=notification.is_read,
                created_at=notification.created_at.isoformat(),
                solicitud_url=notification.solicitud_url
            )
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get(
        "/api/internal-notifications/user/{user_id}",
        response_model=InternalNotificationListResponse,
        tags=["Internal Notifications"],
        summary="Obtener notificaciones de usuario",
        description="Obtiene todas las notificaciones internas de un usuario específico"
    )
    async def get_user_notifications(
        user_id: str,
        limit: Optional[int] = Query(
            None,
            description="Número máximo de notificaciones a devolver",
            ge=1,
            le=100
        ),
        only_unread: bool = Query(
            False,
            description="Si True, solo retorna notificaciones no leídas"
        )
    ):
        """
        Obtiene las notificaciones de un usuario.

        **Query Params:**
        - limit: Número máximo de notificaciones (1-100)
        - only_unread: Si True, solo retorna no leídas

        **Response:**
        ```json
        {
          "total": 10,
          "unread": 3,
          "notifications": [...]
        }
        ```
        """
        try:
            notifications = internal_notification_service.get_user_notifications(
                user_id, limit, only_unread
            )
            unread_count = internal_notification_service.get_unread_count(user_id)

            return InternalNotificationListResponse(
                total=len(notifications),
                unread=unread_count,
                notifications=[
                    InternalNotificationResponse(
                        id=n.id,
                        user_id=n.user_id,
                        solicitud_id=n.solicitud_id,
                        event_type=n.event_type,
                        notification_subject=n.notification_subject,
                        solicitud_subject=n.solicitud_subject,
                        is_read=n.is_read,
                        created_at=n.created_at.isoformat(),
                        solicitud_url=n.solicitud_url
                    )
                    for n in notifications
                ]
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.put(
        "/api/internal-notifications/{notification_id}/read",
        response_model=MarkAsReadResponse,
        tags=["Internal Notifications"],
        summary="Marcar notificación como leída",
        description="Marca una notificación específica como leída"
    )
    async def mark_notification_as_read(notification_id: int):
        """
        Marca una notificación como leída.

        **Args:**
        - notification_id: ID de la notificación

        **Response:**
        ```json
        {
          "status": "success",
          "message": "Notificación marcada como leída"
        }
        ```
        """
        try:
            success = internal_notification_service.mark_as_read(notification_id)

            if not success:
                raise HTTPException(
                    status_code=404,
                    detail=f"Notificación {notification_id} no encontrada"
                )

            return MarkAsReadResponse(
                status="success",
                message="Notificación marcada como leída"
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.put(
        "/api/internal-notifications/user/{user_id}/read-all",
        response_model=MarkAsReadResponse,
        tags=["Internal Notifications"],
        summary="Marcar todas como leídas",
        description="Marca todas las notificaciones de un usuario como leídas"
    )
    async def mark_all_as_read(user_id: str):
        """
        Marca todas las notificaciones de un usuario como leídas.

        **Args:**
        - user_id: ID del usuario

        **Response:**
        ```json
        {
          "status": "success",
          "message": "5 notificaciones marcadas como leídas"
        }
        ```
        """
        try:
            count = internal_notification_service.mark_all_as_read(user_id)

            return MarkAsReadResponse(
                status="success",
                message=f"{count} notificaciones marcadas como leídas"
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get(
        "/api/internal-notifications/user/{user_id}/unread-count",
        response_model=UnreadCountResponse,
        tags=["Internal Notifications"],
        summary="Contador de no leídas",
        description="Obtiene el número de notificaciones no leídas de un usuario"
    )
    async def get_unread_count(user_id: str):
        """
        Obtiene el contador de notificaciones no leídas.

        Útil para mostrar badges en la UI.

        **Response:**
        ```json
        {
          "unread_count": 5
        }
        ```
        """
        try:
            count = internal_notification_service.get_unread_count(user_id)
            return UnreadCountResponse(unread_count=count)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.get(
        "/api/internal-notifications/user/{user_id}/summary",
        response_model=NotificationSummaryResponse,
        tags=["Internal Notifications"],
        summary="Resumen de notificaciones",
        description="Obtiene un resumen estadístico de las notificaciones del usuario"
    )
    async def get_notification_summary(user_id: str):
        """
        Obtiene un resumen de notificaciones.

        **Response:**
        ```json
        {
          "total": 25,
          "unread": 5,
          "recent": [...]
        }
        ```
        """
        try:
            summary = internal_notification_service.get_notification_summary(user_id)
            return NotificationSummaryResponse(**summary)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @app.delete(
        "/api/internal-notifications/{notification_id}",
        response_model=MarkAsReadResponse,
        tags=["Internal Notifications"],
        summary="Eliminar notificación",
        description="Elimina una notificación específica"
    )
    async def delete_notification(notification_id: int):
        """
        Elimina una notificación.

        **Args:**
        - notification_id: ID de la notificación a eliminar

        **Warning:** Esta operación es irreversible
        """
        try:
            success = internal_notification_service.delete_notification(notification_id)

            if not success:
                raise HTTPException(
                    status_code=404,
                    detail=f"Notificación {notification_id} no encontrada"
                )

            return MarkAsReadResponse(
                status="success",
                message="Notificación eliminada correctamente"
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    # Endpoint para la UI del panel de usuario
    @app.get(
        "/user-notifications",
        tags=["UI"],
        summary="Panel de notificaciones del usuario",
        description="Interfaz web para ver notificaciones internas",
        include_in_schema=False
    )
    async def user_notifications_ui():
        """Sirve la interfaz web del panel de notificaciones de usuario"""
        from fastapi.responses import FileResponse
        return FileResponse("static/notifications.html")
