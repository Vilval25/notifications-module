"""
Repositorio base para operaciones SQL comunes
Elimina duplicación de código en repositorios SQL
"""
import sqlite3
from typing import Any, List, Optional, Tuple
from contextlib import contextmanager


class BaseSQLRepository:
    """
    Clase base abstracta para repositorios SQL

    Encapsula la lógica común de:
    - Gestión de conexiones
    - Ejecución de queries
    - Manejo de transacciones
    """

    def __init__(self, db_path: str):
        """
        Inicializa el repositorio base

        Args:
            db_path: Ruta a la base de datos SQLite
        """
        self._db_path = db_path

    @contextmanager
    def _get_connection(self):
        """
        Context manager para obtener una conexión a la base de datos

        Uso:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM table")

        Yields:
            sqlite3.Connection: Conexión a la base de datos
        """
        conn = sqlite3.connect(self._db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    def _execute_query(
        self,
        query: str,
        params: Optional[Tuple] = None
    ) -> List[sqlite3.Row]:
        """
        Ejecuta una query SELECT y retorna los resultados

        Args:
            query: Query SQL a ejecutar
            params: Parámetros de la query (opcional)

        Returns:
            Lista de filas resultado
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.fetchall()

    def _execute_commit(
        self,
        query: str,
        params: Optional[Tuple] = None
    ) -> int:
        """
        Ejecuta una query INSERT/UPDATE/DELETE y retorna el lastrowid

        Args:
            query: Query SQL a ejecutar
            params: Parámetros de la query (opcional)

        Returns:
            ID de la última fila insertada (para INSERT)
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            return cursor.lastrowid

    def _execute_many(
        self,
        query: str,
        params_list: List[Tuple]
    ) -> None:
        """
        Ejecuta múltiples queries en una sola transacción

        Args:
            query: Query SQL a ejecutar
            params_list: Lista de tuplas con parámetros
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(query, params_list)

    def _init_table(self, create_table_sql: str) -> None:
        """
        Crea una tabla si no existe

        Args:
            create_table_sql: SQL de CREATE TABLE
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(create_table_sql)
