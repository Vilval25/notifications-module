"""
Repositorio para gestionar notificaciones internas del sistema
"""

import sqlite3
from typing import List, Optional
from datetime import datetime
from src.domain.internal_notification import InternalNotification
from .i_internal_notification_repository import IInternalNotificationRepository
from .base_sql_repository import BaseSQLRepository


class InternalNotificationRepository(BaseSQLRepository, IInternalNotificationRepository):
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
        super().__init__(db_path)
        self._init_database()

    def _init_database(self):
        """Crea la tabla internal_notifications y sus índices si no existen"""
        # Crear tabla principal
        self._init_table("""
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
        with self._get_connection() as conn:
            cursor = conn.cursor()
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

    def save(self, notification: InternalNotification) -> InternalNotification:
        """
        Guarda una nueva notificación interna

        Args:
            notification: Notificación a guardar

        Returns:
            Notificación guardada con ID asignado
        """
        notification.id = self._execute_commit("""
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

        rows = self._execute_query(query, tuple(params))

        return [self._map_row_to_notification(row) for row in rows]

    def find_by_id(self, notification_id: int) -> Optional[InternalNotification]:
        """
        Obtiene una notificación por su ID

        Args:
            notification_id: ID de la notificación

        Returns:
            Notificación o None si no existe
        """
        rows = self._execute_query("""
            SELECT id, user_id, solicitud_id, event_type, notification_subject,
                   solicitud_subject, is_read, created_at, solicitud_url
            FROM internal_notifications
            WHERE id = ?
        """, (notification_id,))

        if rows:
            return self._map_row_to_notification(rows[0])

        return None

    def mark_as_read(self, notification_id: int) -> bool:
        """
        Marca una notificación como leída

        Args:
            notification_id: ID de la notificación

        Returns:
            True si se actualizó correctamente, False en caso contrario
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE internal_notifications
                SET is_read = 1
                WHERE id = ?
            """, (notification_id,))
            return cursor.rowcount > 0

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
        cutoff_date = datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        cutoff_date = cutoff_date.replace(day=cutoff_date.day - days)

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM internal_notifications
                WHERE user_id = ? AND created_at < ?
            """, (user_id, cutoff_date.isoformat()))
            return cursor.rowcount

    def _map_row_to_notification(self, row: sqlite3.Row) -> InternalNotification:
        """
        Mapea una fila de la BD a un objeto InternalNotification

        Args:
            row: Fila de la base de datos

        Returns:
            Objeto InternalNotification
        """
        return InternalNotification(
            id=row['id'],
            user_id=row['user_id'],
            solicitud_id=row['solicitud_id'],
            event_type=row['event_type'],
            notification_subject=row['notification_subject'],
            solicitud_subject=row['solicitud_subject'],
            is_read=bool(row['is_read']),
            created_at=datetime.fromisoformat(row['created_at']),
            solicitud_url=row['solicitud_url']
        )
