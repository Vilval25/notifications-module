import sqlite3
from typing import List
from datetime import datetime
from ...domain.notification_log import NotificationLog
from ...domain.notification_channel import NotificationChannel
from .i_notification_log_repository import INotificationLogRepository
from .base_sql_repository import BaseSQLRepository


class SqlNotificationLogRepository(BaseSQLRepository, INotificationLogRepository):
    """
    Repositorio de logs de notificaciones usando SQL nativo.

    Responsabilidad: Persistir el historial/auditoría de todas las notificaciones
    enviadas por el sistema (email, SMS, WhatsApp).

    Implementación con SQLite, pero fácilmente adaptable a PostgreSQL, MySQL, etc.
    """

    def __init__(self, db_path: str):
        """
        Inicializa el repositorio con conexión a base de datos

        Args:
            db_path: Ruta a la base de datos SQLite
        """
        super().__init__(db_path)
        self._init_database()

    def _init_database(self) -> None:
        """Crea la tabla de logs si no existe"""
        self._init_table("""
            CREATE TABLE IF NOT EXISTS notification_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recipient TEXT NOT NULL,
                channel TEXT NOT NULL,
                content TEXT NOT NULL,
                status TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                source_module TEXT NOT NULL
            )
        """)

    def save(self, log: NotificationLog) -> None:
        """
        Persiste un log en la base de datos usando SQL nativo

        Args:
            log: Log a guardar
        """
        self._execute_commit("""
            INSERT INTO notification_logs
            (recipient, channel, content, status, timestamp, source_module)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            log.recipient,
            log.channel.value,
            log.content,
            log.status,
            log.timestamp.isoformat(),
            log.source_module
        ))

    def find_by_module(self, module_id: str) -> List[NotificationLog]:
        """
        Busca logs por módulo usando SQL nativo

        Args:
            module_id: ID del módulo (vacío para todos)

        Returns:
            Lista de logs
        """
        if module_id:
            rows = self._execute_query("""
                SELECT * FROM notification_logs
                WHERE source_module = ?
                ORDER BY timestamp DESC
            """, (module_id,))
        else:
            rows = self._execute_query("""
                SELECT * FROM notification_logs
                ORDER BY timestamp DESC
            """)

        return [self._map_row_to_log(row) for row in rows]

    def _map_row_to_log(self, row: sqlite3.Row) -> NotificationLog:
        """
        Mapea una fila de ResultSet a un objeto NotificationLog

        Args:
            row: Fila de la base de datos

        Returns:
            Objeto NotificationLog
        """
        return NotificationLog(
            id=row['id'],
            recipient=row['recipient'],
            channel=NotificationChannel(row['channel']),
            content=row['content'],
            status=row['status'],
            timestamp=datetime.fromisoformat(row['timestamp']),
            source_module=row['source_module']
        )
