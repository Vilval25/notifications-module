from abc import ABC, abstractmethod
from typing import Dict, Any


class ITemplateEngine(ABC):
    """Interfaz para motores de plantillas"""

    @abstractmethod
    def render(self, template_name: str, params: Dict[str, Any]) -> str:
        """
        Renderiza una plantilla con los parámetros dados

        Args:
            template_name: Nombre del archivo de plantilla
            params: Parámetros para reemplazar en la plantilla

        Returns:
            Contenido renderizado
        """
        pass
