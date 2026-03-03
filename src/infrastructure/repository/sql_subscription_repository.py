"""
Repositorio para gestionar suscripciones de notificaciones de usuario
"""
import sqlite3
from typing import List, Optional
from datetime import datetime
from src.domain.subscription import UserNotificationSubscription
from .i_subscription_repository import ISubscriptionRepository


class SubscriptionRepository(ISubscriptionRepository):
    """
    Repositorio para operaciones CRUD de suscripciones de notificaciones
    """

    def __init__(self, db_path: str = "notifications.db"):
        self.db_path = db_path
        self._create_table()

    def _create_table(self):
        """Crea la tabla de suscripciones si no existe"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
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
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_subscriptions_user
            ON notification_subscriptions(user_id)
        ''')
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_subscriptions_event
            ON notification_subscriptions(event_type)
        ''')
        conn.commit()
        conn.close()

    def save(self, subscription: UserNotificationSubscription) -> UserNotificationSubscription:
        """
        Guarda o actualiza una suscripción
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        subscription.updated_at = datetime.now()

        try:
            cursor.execute('''
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

            subscription.id = cursor.lastrowid
            conn.commit()
            return subscription
        finally:
            conn.close()

    def find_by_user(self, user_id: str) -> List[UserNotificationSubscription]:
        """
        Obtiene todas las suscripciones de un usuario
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT id, user_id, event_type, email_enabled, sms_enabled,
                       whatsapp_enabled, created_at, updated_at
                FROM notification_subscriptions
                WHERE user_id = ?
                ORDER BY event_type
            ''', (user_id,))

            rows = cursor.fetchall()
            return [self._row_to_subscription(row) for row in rows]
        finally:
            conn.close()

    def find_by_user_and_event(self, user_id: str, event_type: str) -> Optional[UserNotificationSubscription]:
        """
        Obtiene la suscripción de un usuario para un evento específico
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                SELECT id, user_id, event_type, email_enabled, sms_enabled,
                       whatsapp_enabled, created_at, updated_at
                FROM notification_subscriptions
                WHERE user_id = ? AND event_type = ?
            ''', (user_id, event_type))

            row = cursor.fetchone()
            return self._row_to_subscription(row) if row else None
        finally:
            conn.close()

    def delete(self, user_id: str, event_type: str) -> bool:
        """
        Elimina una suscripción
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                DELETE FROM notification_subscriptions
                WHERE user_id = ? AND event_type = ?
            ''', (user_id, event_type))

            deleted = cursor.rowcount > 0
            conn.commit()
            return deleted
        finally:
            conn.close()

    def _row_to_subscription(self, row) -> UserNotificationSubscription:
        """Convierte una fila de base de datos a una entidad UserNotificationSubscription"""
        return UserNotificationSubscription(
            id=row[0],
            user_id=row[1],
            event_type=row[2],
            email_enabled=bool(row[3]),
            sms_enabled=bool(row[4]),
            whatsapp_enabled=bool(row[5]),
            created_at=datetime.fromisoformat(row[6]),
            updated_at=datetime.fromisoformat(row[7])
        )
