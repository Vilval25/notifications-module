"""
Servicio para gestión CRUD de plantillas Handlebars
"""

import os
import json
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
from pybars import Compiler


class TemplateService:
    """Servicio para gestión CRUD de plantillas Handlebars"""

    def __init__(self, templates_path: str, event_repository=None):
        """
        Inicializa el servicio de templates

        Args:
            templates_path: Ruta a la carpeta de plantillas
            event_repository: Repositorio de eventos de plantillas (opcional)
        """
        self._templates_path = templates_path
        self._compiler = Compiler()
        self._event_repository = event_repository

        # Crear carpeta si no existe
        if not os.path.exists(templates_path):
            os.makedirs(templates_path)

    def _parse_metadata(self, content: str) -> Dict[str, Any]:
        """
        Extrae metadata JSON del contenido de una plantilla

        El metadata está en formato:
        <!-- META:START
        {
          "subject": "Asunto del email",
          "event_type": "tramite_aprobado",
          "variables": ["nombre", "email", "enlace", "telefono"]
        }
        META:END -->

        Args:
            content: Contenido completo del archivo .hbs

        Returns:
            Dict con metadata o valores por defecto si no existe
        """
        # Buscar bloque de metadata
        pattern = r'<!--\s*META:START\s*\n(.*?)\nMETA:END\s*-->'
        match = re.search(pattern, content, re.DOTALL)

        if match:
            try:
                metadata_json = match.group(1).strip()
                metadata = json.loads(metadata_json)
                return metadata
            except json.JSONDecodeError as e:
                print(f"Error parseando metadata JSON: {e}")
                return self._get_default_metadata()
        else:
            # No hay metadata, retornar valores por defecto
            return self._get_default_metadata()

    def _get_default_metadata(self) -> Dict[str, Any]:
        """
        Retorna metadata por defecto para plantillas sin metadata

        Returns:
            Dict con metadata por defecto
        """
        return {
            'subject': 'Sin asunto',
            'event_type': None,
            'variables': ['nombre', 'email', 'enlace', 'telefono']
        }

    def _strip_metadata(self, content: str) -> str:
        """
        Elimina el bloque de metadata del contenido de la plantilla

        Args:
            content: Contenido completo del archivo .hbs

        Returns:
            Contenido sin metadata
        """
        pattern = r'<!--\s*META:START\s*\n.*?\nMETA:END\s*-->\s*\n?'
        return re.sub(pattern, '', content, flags=re.DOTALL).strip()

    def _build_template_with_metadata(self, content: str, subject: str,
                                     event_type: Optional[str] = None) -> str:
        """
        Construye el contenido completo de una plantilla con metadata

        Args:
            content: Contenido HTML/Handlebars (sin metadata)
            subject: Asunto del email
            event_type: Tipo de evento (opcional)

        Returns:
            Contenido completo con bloque de metadata
        """
        metadata = {
            'subject': subject,
            'event_type': event_type,
            'variables': ['nombre', 'email', 'enlace', 'telefono']
        }

        metadata_json = json.dumps(metadata, indent=2, ensure_ascii=False)

        return f"""<!-- META:START
{metadata_json}
META:END -->
{content}"""

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

    def list_templates_with_status(self) -> List[Dict[str, Any]]:
        """
        Lista todas las plantillas con metadata y estado

        Returns:
            Lista de dicts con información completa de cada plantilla
        """
        try:
            templates = []
            files = os.listdir(self._templates_path)

            for filename in sorted(files):
                if not filename.endswith('.hbs'):
                    continue

                name = filename[:-4]
                template_data = self.get_template(name)

                if template_data:
                    templates.append({
                        'name': name,
                        'subject': template_data.get('subject', 'Sin asunto'),
                        'event_type': template_data.get('event_type'),
                        'is_active': template_data.get('is_active', False),
                        'modified': template_data.get('modified')
                    })

            return templates
        except Exception as e:
            print(f"Error listando plantillas con estado: {e}")
            return []

    def get_template(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene una plantilla por nombre con metadata y estado

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
                full_content = f.read()

            # Parsear metadata
            metadata = self._parse_metadata(full_content)

            # Obtener contenido sin metadata
            content = self._strip_metadata(full_content)

            stats = os.stat(template_path)
            modified = datetime.fromtimestamp(stats.st_mtime)

            # Verificar si está activa (si hay event_repository)
            is_active = False
            if self._event_repository:
                is_active = self._event_repository.check_template_in_use(name)

            return {
                'name': name,
                'content': content,
                'subject': metadata.get('subject', 'Sin asunto'),
                'event_type': metadata.get('event_type'),  # Siempre usar event_type de metadata
                'is_active': is_active,
                'size': stats.st_size,
                'modified': modified.isoformat()
            }
        except Exception as e:
            print(f"Error obteniendo plantilla {name}: {e}")
            return None

    def create_template(self, name: str, content: str, subject: str,
                        event_type: Optional[str] = None) -> bool:
        """
        Crea una nueva plantilla con metadata (sin activarla automáticamente)

        Args:
            name: Nombre de la plantilla sin extensión
            content: Contenido Handlebars (sin metadata)
            subject: Asunto del email
            event_type: Tipo de evento al que pertenece la plantilla

        Returns:
            True si se creó correctamente, False si ya existe o hay error

        Nota:
            La plantilla se crea con el evento asignado en su metadata,
            pero NO se activa automáticamente. El usuario debe activarla
            manualmente desde la interfaz.
        """
        try:
            template_path = os.path.join(self._templates_path, f"{name}.hbs")

            # Verificar que no exista
            if os.path.exists(template_path):
                return False

            # Validar sintaxis antes de guardar (solo el contenido, sin metadata)
            self._compiler.compile(content)

            # Construir contenido completo con metadata
            full_content = self._build_template_with_metadata(content, subject, event_type)

            # Guardar archivo
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(full_content)

            # NO activar automáticamente - el usuario debe hacerlo manualmente

            return True
        except Exception as e:
            print(f"Error creando plantilla {name}: {e}")
            return False

    def update_template(self, name: str, content: str, subject: str,
                        event_type: Optional[str] = None) -> bool:
        """
        Actualiza una plantilla existente

        Args:
            name: Nombre de la plantilla sin extensión
            content: Nuevo contenido Handlebars (sin metadata)
            subject: Nuevo asunto del email
            event_type: Nuevo tipo de evento (opcional, solo si no está activa)

        Returns:
            True si se actualizó correctamente, False si no existe o hay error

        Raises:
            ValueError: Si intenta cambiar el event_type de una plantilla activa
        """
        try:
            template_path = os.path.join(self._templates_path, f"{name}.hbs")

            # Verificar que exista
            if not os.path.exists(template_path):
                return False

            # Leer plantilla actual
            with open(template_path, 'r', encoding='utf-8') as f:
                old_content = f.read()

            old_metadata = self._parse_metadata(old_content)

            # Si se intenta cambiar event_type, verificar que no esté activa
            event_changed = False
            if event_type is not None and event_type != old_metadata.get('event_type'):
                if self._event_repository and self._event_repository.check_template_in_use(name):
                    raise ValueError("No se puede cambiar el evento de una plantilla que está en uso")
                final_event_type = event_type
                event_changed = True
            else:
                # Preservar event_type existente
                final_event_type = old_metadata.get('event_type')

            # Validar sintaxis antes de guardar (solo el contenido, sin metadata)
            self._compiler.compile(content)

            # Construir contenido completo con metadata actualizada
            full_content = self._build_template_with_metadata(content, subject, final_event_type)

            # Guardar archivo
            with open(template_path, 'w', encoding='utf-8') as f:
                f.write(full_content)

            # NO activar automáticamente - solo actualizar la metadata
            # El usuario debe activar manualmente desde la interfaz

            return True
        except ValueError:
            raise
        except Exception as e:
            print(f"Error actualizando plantilla {name}: {e}")
            return False

    def delete_template(self, name: str) -> bool:
        """
        Elimina una plantilla si no está activa

        Args:
            name: Nombre de la plantilla sin extensión

        Returns:
            True si se eliminó correctamente, False si no existe o hay error

        Raises:
            ValueError: Si la plantilla está activa y no se puede eliminar
        """
        try:
            template_path = os.path.join(self._templates_path, f"{name}.hbs")

            # Verificar que exista
            if not os.path.exists(template_path):
                return False

            # Verificar que no esté activa (si hay event_repository)
            if self._event_repository:
                if self._event_repository.check_template_in_use(name):
                    raise ValueError("No se puede eliminar una plantilla que está en uso")

            # Eliminar archivo
            os.remove(template_path)
            return True
        except ValueError:
            raise
        except Exception as e:
            print(f"Error eliminando plantilla {name}: {e}")
            return False

    def rename_template(self, old_name: str, new_name: str) -> bool:
        """
        Renombra una plantilla

        Args:
            old_name: Nombre actual de la plantilla sin extensión
            new_name: Nuevo nombre de la plantilla sin extensión

        Returns:
            True si se renombró correctamente, False si hay error

        Raises:
            ValueError: Si el nuevo nombre ya existe
        """
        try:
            old_path = os.path.join(self._templates_path, f"{old_name}.hbs")
            new_path = os.path.join(self._templates_path, f"{new_name}.hbs")

            # Verificar que la plantilla antigua exista
            if not os.path.exists(old_path):
                return False

            # Verificar que el nuevo nombre no exista
            if os.path.exists(new_path):
                raise ValueError(f"Ya existe una plantilla con el nombre '{new_name}'")

            # Renombrar archivo
            os.rename(old_path, new_path)

            # Si está activa, actualizar en la tabla de eventos
            if self._event_repository:
                # Obtener todos los eventos para ver si esta plantilla está asignada
                events = self._event_repository.get_all_events()
                for event in events:
                    if event.template_name == old_name and event.is_active:
                        # Actualizar el nombre de la plantilla en el evento
                        self._event_repository.activate_template_for_event(event.event_type, new_name)

            return True
        except ValueError:
            raise
        except Exception as e:
            print(f"Error renombrando plantilla {old_name} a {new_name}: {e}")
            return False

    def validate_syntax(self, content: str) -> Dict[str, Any]:
        """
        Valida la sintaxis de una plantilla Handlebars

        Args:
            content: Contenido Handlebars a validar (puede incluir metadata)

        Returns:
            Dict con 'valid' (bool) y 'error' (str o None)
        """
        try:
            # Stripear metadata si existe
            clean_content = self._strip_metadata(content)

            self._compiler.compile(clean_content)
            return {'valid': True, 'error': None}
        except Exception as e:
            return {'valid': False, 'error': str(e)}

    def preview_template(self, content: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Renderiza una plantilla con parámetros de prueba

        Args:
            content: Contenido Handlebars (puede incluir metadata)
            params: Parámetros para renderizar

        Returns:
            Dict con 'rendered', 'valid' y 'error'
        """
        try:
            # Stripear metadata si existe
            clean_content = self._strip_metadata(content)

            template = self._compiler.compile(clean_content)
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

    def get_active_template_for_event(self, event_type: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene la plantilla activa para un evento específico

        Args:
            event_type: Tipo de evento (ej: 'tramite_aprobado', 'creacion_cuenta')

        Returns:
            Dict con información de la plantilla activa o None si no hay plantilla activa
            Incluye: name, subject, event_type, content

        Raises:
            ValueError: Si no hay event_repository configurado o no hay plantilla activa
        """
        if not self._event_repository:
            raise ValueError("Event repository no configurado")

        # Obtener el nombre de la plantilla activa para el evento (retorna string)
        active_template_name = self._event_repository.get_active_template_for_event(event_type)

        if not active_template_name:
            raise ValueError(f"No hay plantilla activa para el evento '{event_type}'")

        # Cargar la información completa de la plantilla usando el nombre
        template_data = self.get_template(active_template_name)

        if not template_data:
            raise ValueError(f"Plantilla '{active_template_name}' no encontrada")

        return template_data
