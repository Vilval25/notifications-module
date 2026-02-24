"""
Servicio para gestión CRUD de plantillas Handlebars
"""

import os
from typing import List, Dict, Any, Optional
from datetime import datetime
from pybars import Compiler


class TemplateService:
    """Servicio para gestión CRUD de plantillas Handlebars"""

    def __init__(self, templates_path: str):
        """
        Inicializa el servicio de templates

        Args:
            templates_path: Ruta a la carpeta de plantillas
        """
        self._templates_path = templates_path
        self._compiler = Compiler()

        # Crear carpeta si no existe
        if not os.path.exists(templates_path):
            os.makedirs(templates_path)

    def list_templates(self) -> List[str]:
        """
        Lista todas las plantillas disponibles

        Returns:
            Lista de nombres de plantillas sin extensión .hbs
        """
        try:
            files = os.listdir(self._templates_path)
            templates = [
                f[:-4] for f in files
                if f.endswith('.hbs')
            ]
            return sorted(templates)
        except Exception as e:
            print(f"Error listando plantillas: {e}")
            return []

    def get_template(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene una plantilla por nombre

        Args:
            name: Nombre de la plantilla sin extensión

        Returns:
            Dict con información de la plantilla o None si no existe
        """
        try:
            template_path = os.path.join(self._templates_path, f"{name}.hbs")

            if not os.path.exists(template_path):
                return None

            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()

            stats = os.stat(template_path)
            modified = datetime.fromtimestamp(stats.st_mtime)

            return {
                'name': name,
                'content': content,
                'size': stats.st_size,
                'modified': modified.isoformat()
            }
        except Exception as e:
            print(f"Error obteniendo plantilla {name}: {e}")
            return None

    def create_template(self, name: str, content: str) -> bool:
        """
        Crea una nueva plantilla

        Args:
            name: Nombre de la plantilla sin extensión
            content: Contenido Handlebars

        Returns:
            True si se creó correctamente, False si ya existe o hay error
        """
        try:
            template_path = os.path.join(self._templates_path, f"{name}.hbs")

            # Verificar que no exista
            if os.path.exists(template_path):
                return False

            # Validar sintaxis antes de guardar
            self._compiler.compile(content)

            # Guardar archivo
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(content)

            return True
        except Exception as e:
            print(f"Error creando plantilla {name}: {e}")
            return False

    def update_template(self, name: str, content: str) -> bool:
        """
        Actualiza una plantilla existente

        Args:
            name: Nombre de la plantilla sin extensión
            content: Nuevo contenido Handlebars

        Returns:
            True si se actualizó correctamente, False si no existe o hay error
        """
        try:
            template_path = os.path.join(self._templates_path, f"{name}.hbs")

            # Verificar que exista
            if not os.path.exists(template_path):
                return False

            # Validar sintaxis antes de guardar
            self._compiler.compile(content)

            # Guardar archivo
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(content)

            return True
        except Exception as e:
            print(f"Error actualizando plantilla {name}: {e}")
            return False

    def delete_template(self, name: str) -> bool:
        """
        Elimina una plantilla

        Args:
            name: Nombre de la plantilla sin extensión

        Returns:
            True si se eliminó correctamente, False si no existe o hay error
        """
        try:
            template_path = os.path.join(self._templates_path, f"{name}.hbs")

            # Verificar que exista
            if not os.path.exists(template_path):
                return False

            # Eliminar archivo
            os.remove(template_path)
            return True
        except Exception as e:
            print(f"Error eliminando plantilla {name}: {e}")
            return False

    def validate_syntax(self, content: str) -> Dict[str, Any]:
        """
        Valida la sintaxis de una plantilla Handlebars

        Args:
            content: Contenido Handlebars a validar

        Returns:
            Dict con 'valid' (bool) y 'error' (str o None)
        """
        try:
            self._compiler.compile(content)
            return {'valid': True, 'error': None}
        except Exception as e:
            return {'valid': False, 'error': str(e)}

    def preview_template(self, content: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Renderiza una plantilla con parámetros de prueba

        Args:
            content: Contenido Handlebars
            params: Parámetros para renderizar

        Returns:
            Dict con 'rendered', 'valid' y 'error'
        """
        try:
            template = self._compiler.compile(content)
            rendered = template(params)
            return {
                'rendered': rendered,
                'valid': True,
                'error': None
            }
        except Exception as e:
            return {
                'rendered': '',
                'valid': False,
                'error': str(e)
            }
