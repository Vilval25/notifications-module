"""
Repositorio para gestionar suscripciones de notificaciones de usuario
"""
import sqlite3
from typing import List, Optional
from datetime import datetime
from src.domain.subscription import UserNotificationSubscription
from .i_subscription_repository import ISubscriptionRepository
from .base_sql_repository import BaseSQLRepository


class SubscriptionRepository(BaseSQLRepository, ISubscriptionRepository):
    """
    Repositorio para operaciones CRUD de suscripciones de notificaciones
    """

    def __init__(self, db_path: str = "notifications.db"):
        super().__init__(db_path)
        self._create_table()

    def _create_table(self):
        """Crea la tabla de suscripciones y sus índices si no existen"""
        self._init_table('''
            CREATE TABLE IF NOT EXISTS notification_subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT NOT NULL,
                event_type TEXT NOT NULL,
                email_enabled INTEGER DEFAULT 0,
                sms_enabled INTEGER DEFAULT 0,
                whatsapp_enabled INTEGER DEFAULT 0,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                UNIQUE(user_id, event_type)
            )
        ''')

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_subscriptions_user
                ON notification_subscriptions(user_id)
            ''')
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_subscriptions_event
                ON notification_subscriptions(event_type)
            ''')

    def save(self, subscription: UserNotificationSubscription) -> UserNotificationSubscription:
        """
        Guarda o actualiza una suscripción
        """
        subscription.updated_at = datetime.now()

        subscription.id = self._execute_commit('''
            INSERT INTO notification_subscriptions
            (user_id, event_type, email_enabled, sms_enabled, whatsapp_enabled, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id, event_type) DO UPDATE SET
                email_enabled = excluded.email_enabled,
                sms_enabled = excluded.sms_enabled,
                whatsapp_enabled = excluded.whatsapp_enabled,
                updated_at = excluded.updated_at
        ''', (
            subscription.user_id,
            subscription.event_type,
            1 if subscription.email_enabled else 0,
            1 if subscription.sms_enabled else 0,
            1 if subscription.whatsapp_enabled else 0,
            subscription.created_at.isoformat(),
            subscription.updated_at.isoformat()
        ))

        return subscription

    def find_by_user(self, user_id: str) -> List[UserNotificationSubscription]:
        """
        Obtiene todas las suscripciones de un usuario
        """
        rows = self._execute_query('''
            SELECT id, user_id, event_type, email_enabled, sms_enabled,
                   whatsapp_enabled, created_at, updated_at
            FROM notification_subscriptions
            WHERE user_id = ?
            ORDER BY event_type
        ''', (user_id,))

        return [self._row_to_subscription(row) for row in rows]

    def find_by_user_and_event(self, user_id: str, event_type: str) -> Optional[UserNotificationSubscription]:
        """
        Obtiene la suscripción de un usuario para un evento específico
        """
        rows = self._execute_query('''
            SELECT id, user_id, event_type, email_enabled, sms_enabled,
                   whatsapp_enabled, created_at, updated_at
            FROM notification_subscriptions
            WHERE user_id = ? AND event_type = ?
        ''', (user_id, event_type))

        return self._row_to_subscription(rows[0]) if rows else None

    def delete(self, user_id: str, event_type: str) -> bool:
        """
        Elimina una suscripción
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM notification_subscriptions
                WHERE user_id = ? AND event_type = ?
            ''', (user_id, event_type))
            return cursor.rowcount > 0

    def _row_to_subscription(self, row: sqlite3.Row) -> UserNotificationSubscription:
        """Convierte una fila de base de datos a una entidad UserNotificationSubscription"""
        return UserNotificationSubscription(
            id=row['id'],
            user_id=row['user_id'],
            event_type=row['event_type'],
            email_enabled=bool(row['email_enabled']),
            sms_enabled=bool(row['sms_enabled']),
            whatsapp_enabled=bool(row['whatsapp_enabled']),
            created_at=datetime.fromisoformat(row['created_at']),
            updated_at=datetime.fromisoformat(row['updated_at'])
        )
