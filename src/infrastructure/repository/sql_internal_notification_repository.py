"""
Repositorio para gestionar notificaciones internas del sistema
"""

import sqlite3
from typing import List, Optional
from datetime import datetime
from src.domain.internal_notification import InternalNotification
from .i_internal_notification_repository import IInternalNotificationRepository


class InternalNotificationRepository(IInternalNotificationRepository):
    """
    Repositorio para operaciones CRUD sobre notificaciones internas

    Maneja la persistencia de notificaciones que se muestran en el panel de usuario
    """

    def __init__(self, db_path: str):
        """
        Inicializa el repositorio

        Args:
            db_path: Ruta a la base de datos SQLite
        """
        self._db_path = db_path
        self._init_database()

    def _init_database(self):
        """Crea la tabla internal_notifications si no existe"""
        conn = sqlite3.connect(self._db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS internal_notifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                solicitud_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                notification_subject TEXT NOT NULL,
                solicitud_subject TEXT NOT NULL,
                is_read INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                solicitud_url TEXT
            )
        """)

        # Crear índices para búsquedas eficientes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_id
            ON internal_notifications(user_id)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_solicitud_id
            ON internal_notifications(solicitud_id)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_is_read
            ON internal_notifications(is_read)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_created_at
            ON internal_notifications(created_at DESC)
        """)

        conn.commit()
        conn.close()

    def save(self, notification: InternalNotification) -> InternalNotification:
        """
        Guarda una nueva notificación interna

        Args:
            notification: Notificación a guardar

        Returns:
            Notificación guardada con ID asignado
        """
        conn = sqlite3.connect(self._db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO internal_notifications
            (user_id, solicitud_id, event_type, notification_subject,
             solicitud_subject, is_read, created_at, solicitud_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            notification.user_id,
            notification.solicitud_id,
            notification.event_type,
            notification.notification_subject,
            notification.solicitud_subject,
            1 if notification.is_read else 0,
            notification.created_at.isoformat(),
            notification.solicitud_url
        ))

        notification.id = cursor.lastrowid
        conn.commit()
        conn.close()

        return notification

    def find_by_user(self, user_id: str, limit: Optional[int] = None,
                     only_unread: bool = False) -> List[InternalNotification]:
        """
        Obtiene todas las notificaciones de un usuario

        Args:
            user_id: ID del usuario
            limit: Límite de resultados (opcional)
            only_unread: Si True, solo retorna notificaciones no leídas

        Returns:
            Lista de notificaciones ordenadas por fecha descendente
        """
        conn = sqlite3.connect(self._db_path)
        cursor = conn.cursor()

        query = """
            SELECT id, user_id, solicitud_id, event_type, notification_subject,
                   solicitud_subject, is_read, created_at, solicitud_url
            FROM internal_notifications
            WHERE user_id = ?
        """

        params = [user_id]

        if only_unread:
            query += " AND is_read = 0"

        query += " ORDER BY created_at DESC"

        if limit:
            query += " LIMIT ?"
            params.append(limit)

        cursor.execute(query, params)

        notifications = []
        for row in cursor.fetchall():
            notifications.append(InternalNotification(
                id=row[0],
                user_id=row[1],
                solicitud_id=row[2],
                event_type=row[3],
                notification_subject=row[4],
                solicitud_subject=row[5],
                is_read=bool(row[6]),
                created_at=datetime.fromisoformat(row[7]),
                solicitud_url=row[8]
            ))

        conn.close()
        return notifications

    def find_by_id(self, notification_id: int) -> Optional[InternalNotification]:
        """
        Obtiene una notificación por su ID

        Args:
            notification_id: ID de la notificación

        Returns:
            Notificación o None si no existe
        """
        conn = sqlite3.connect(self._db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, user_id, solicitud_id, event_type, notification_subject,
                   solicitud_subject, is_read, created_at, solicitud_url
            FROM internal_notifications
            WHERE id = ?
        """, (notification_id,))

        row = cursor.fetchone()
        conn.close()

        if row:
            return InternalNotification(
                id=row[0],
                user_id=row[1],
                solicitud_id=row[2],
                event_type=row[3],
                notification_subject=row[4],
                solicitud_subject=row[5],
                is_read=bool(row[6]),
                created_at=datetime.fromisoformat(row[7]),
                solicitud_url=row[8]
            )

        return None

    def mark_as_read(self, notification_id: int) -> bool:
        """
        Marca una notificación como leída

        Args:
            notification_id: ID de la notificación

        Returns:
            True si se actualizó correctamente, False en caso contrario
        """
        conn = sqlite3.connect(self._db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE internal_notifications
            SET is_read = 1
            WHERE id = ?
        """, (notification_id,))

        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()

        return rows_affected > 0

    def mark_all_as_read(self, user_id: str) -> int:
        """
        Marca todas las notificaciones de un usuario como leídas

        Args:
            user_id: ID del usuario

        Returns:
            Número de notificaciones actualizadas
        """
        conn = sqlite3.connect(self._db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE internal_notifications
            SET is_read = 1
            WHERE user_id = ? AND is_read = 0
        """, (user_id,))

        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()

        return rows_affected

    def count_unread(self, user_id: str) -> int:
        """
        Cuenta las notificaciones no leídas de un usuario

        Args:
            user_id: ID del usuario

        Returns:
            Número de notificaciones no leídas
        """
        conn = sqlite3.connect(self._db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*)
            FROM internal_notifications
            WHERE user_id = ? AND is_read = 0
        """, (user_id,))

        count = cursor.fetchone()[0]
        conn.close()

        return count

    def delete(self, notification_id: int) -> bool:
        """
        Elimina una notificación

        Args:
            notification_id: ID de la notificación

        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        conn = sqlite3.connect(self._db_path)
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM internal_notifications
            WHERE id = ?
        """, (notification_id,))

        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()

        return rows_affected > 0

    def delete_old_notifications(self, user_id: str, days: int = 30) -> int:
        """
        Elimina notificaciones antiguas de un usuario

        Args:
            user_id: ID del usuario
            days: Días de antigüedad para eliminar (default: 30)

        Returns:
            Número de notificaciones eliminadas
        """
        conn = sqlite3.connect(self._db_path)
        cursor = conn.cursor()

        cutoff_date = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        cutoff_date = cutoff_date.replace(day=cutoff_date.day - days)

        cursor.execute("""
            DELETE FROM internal_notifications
            WHERE user_id = ? AND created_at < ?
        """, (user_id, cutoff_date.isoformat()))

        rows_affected = cursor.rowcount
        conn.commit()
        conn.close()

        return rows_affected
