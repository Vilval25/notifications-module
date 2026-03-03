"""
Repositorio para gestionar eventos de plantillas
"""

import sqlite3
from typing import List, Optional
from datetime import datetime
from src.domain.template_event import TemplateEvent
from .i_template_event_repository import ITemplateEventRepository


class TemplateEventRepository(ITemplateEventRepository):
    """
    Repositorio para gestionar la asignación de plantillas a eventos del sistema

    Implementa el patrón Repository para operaciones CRUD sobre template_events
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
        """Crea la tabla template_events si no existe e inserta eventos fijos"""
        conn = sqlite3.connect(self._db_path)
        cursor = conn.cursor()

        # Crear tabla
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS template_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT UNIQUE NOT NULL,
                template_name TEXT NOT NULL,
                is_active INTEGER DEFAULT 1,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)

        # Crear índices para búsquedas eficientes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_event_type
            ON template_events(event_type)
        """)

        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_template_name
            ON template_events(template_name)
        """)

        # Insertar eventos fijos si no existen
        now = datetime.now().isoformat()
        events = [
            ('tramite_registrado', 'notificacion'),
            ('tramite_observado', 'notificacion'),
            ('tramite_aprobado', 'confirmacion'),
            ('tramite_rechazado', 'notificacion'),
            ('confirmacion_cambio_password', 'bienvenida'),
            ('comprobante_pago', 'notificacion'),
            ('creacion_cuenta', 'bienvenida')
        ]

        for event_type, template_name in events:
            cursor.execute("""
                INSERT OR IGNORE INTO template_events
                (event_type, template_name, is_active, created_at, updated_at)
                VALUES (?, ?, 1, ?, ?)
            """, (event_type, template_name, now, now))

        conn.commit()
        conn.close()

    def get_all_events(self) -> List[TemplateEvent]:
        """
        Obtiene todos los eventos con sus plantillas asignadas

        Returns:
            Lista de objetos TemplateEvent
        """
        conn = sqlite3.connect(self._db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, event_type, template_name, is_active, created_at, updated_at
            FROM template_events
            ORDER BY event_type
        """)

        events = []
        for row in cursor.fetchall():
            events.append(TemplateEvent(
                id=row[0],
                event_type=row[1],
                template_name=row[2],
                is_active=bool(row[3]),
                created_at=datetime.fromisoformat(row[4]),
                updated_at=datetime.fromisoformat(row[5])
            ))

        conn.close()
        return events

    def get_event_by_type(self, event_type: str) -> Optional[TemplateEvent]:
        """
        Obtiene un evento específico por su tipo

        Args:
            event_type: Tipo de evento a buscar

        Returns:
            Objeto TemplateEvent o None si no existe
        """
        conn = sqlite3.connect(self._db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id, event_type, template_name, is_active, created_at, updated_at
            FROM template_events
            WHERE event_type = ?
        """, (event_type,))

        row = cursor.fetchone()
        conn.close()

        if row:
            return TemplateEvent(
                id=row[0],
                event_type=row[1],
                template_name=row[2],
                is_active=bool(row[3]),
                created_at=datetime.fromisoformat(row[4]),
                updated_at=datetime.fromisoformat(row[5])
            )

        return None

    def activate_template_for_event(self, event_type: str, template_name: str) -> bool:
        """
        Activa una plantilla para un evento específico
        Automáticamente desactiva la plantilla anterior para ese evento

        Args:
            event_type: Tipo de evento
            template_name: Nombre de la plantilla a activar

        Returns:
            True si la operación fue exitosa, False en caso contrario
        """
        try:
            conn = sqlite3.connect(self._db_path)
            cursor = conn.cursor()
            now = datetime.now().isoformat()

            # Iniciar transacción
            cursor.execute("BEGIN TRANSACTION")

            # Actualizar: marcar nueva plantilla como activa para el evento
            cursor.execute("""
                UPDATE template_events
                SET template_name = ?,
                    is_active = 1,
                    updated_at = ?
                WHERE event_type = ?
            """, (template_name, now, event_type))

            # Commit transacción
            conn.commit()
            conn.close()
            return True

        except Exception as e:
            print(f"Error activando plantilla: {e}")
            if conn:
                conn.rollback()
                conn.close()
            return False

    def check_template_in_use(self, template_name: str) -> bool:
        """
        Verifica si una plantilla está activa para algún evento

        Args:
            template_name: Nombre de la plantilla a verificar

        Returns:
            True si la plantilla está en uso, False en caso contrario
        """
        conn = sqlite3.connect(self._db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*)
            FROM template_events
            WHERE template_name = ? AND is_active = 1
        """, (template_name,))

        count = cursor.fetchone()[0]
        conn.close()

        return count > 0

    def get_active_template_for_event(self, event_type: str) -> Optional[str]:
        """
        Obtiene el nombre de la plantilla activa para un evento

        Args:
            event_type: Tipo de evento

        Returns:
            Nombre de la plantilla activa o None
        """
        conn = sqlite3.connect(self._db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT template_name
            FROM template_events
            WHERE event_type = ? AND is_active = 1
        """, (event_type,))

        row = cursor.fetchone()
        conn.close()

        return row[0] if row else None

    def get_events_by_template(self, template_name: str) -> List[str]:
        """
        Obtiene los eventos que están asignados a una plantilla

        Args:
            template_name: Nombre de la plantilla

        Returns:
            Lista de tipos de eventos asignados a esta plantilla
        """
        conn = sqlite3.connect(self._db_path)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT event_type
            FROM template_events
            WHERE template_name = ? AND is_active = 1
        """, (template_name,))

        events = [row[0] for row in cursor.fetchall()]
        conn.close()

        return events
