import os
from typing import Dict, Any
from pybars import Compiler
from .i_template_engine import ITemplateEngine


class HandlebarsEngine(ITemplateEngine):
    """Motor de plantillas usando Handlebars (pybars)"""

    def __init__(self, template_path: str):
        """
        Inicializa el motor de plantillas

        Args:
            template_path: Ruta a la carpeta de plantillas
        """
        self._template_path = template_path
        self._compiler = Compiler()

    def render(self, template_name: str, params: Dict[str, Any]) -> str:
        """
        Renderiza una plantilla Handlebars con los parámetros dados

        Args:
            template_name: Nombre del archivo de plantilla
            params: Parámetros para reemplazar en la plantilla

        Returns:
            Contenido renderizado
        """
        try:
            template_file = os.path.join(self._template_path, f"{template_name}.hbs")

            print(f"[TEMPLATE] Renderizando plantilla: {template_name}")
            print(f"   Ruta: {template_file}")

            if not os.path.exists(template_file):
                print(f"   [NOT FOUND] Plantilla no encontrada")
                raise FileNotFoundError(f"Template not found: {template_file}")

            with open(template_file, 'r', encoding='utf-8') as f:
                template_content = f.read()

            print(f"   [LOADED] Plantilla cargada ({len(template_content)} caracteres)")

            template = self._compiler.compile(template_content)
            result = template(params)

            print(f"   [RENDERED] Plantilla renderizada ({len(result)} caracteres)")
            return result

        except Exception as e:
            print(f"   [ERROR] Error renderizando plantilla: {type(e).__name__}: {e}")
            raise
