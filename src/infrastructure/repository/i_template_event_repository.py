"""
Interfaz para repositorio de eventos de plantillas
"""
from abc import ABC, abstractmethod
from typing import List, Optional
from src.domain.template_event import TemplateEvent


class ITemplateEventRepository(ABC):
    """
    Interfaz para repositorio de asignación de plantillas a eventos

    Responsabilidad: Gestionar el mapeo entre tipos de eventos del sistema
    y las plantillas Handlebars que se deben usar para cada evento.
    Solo puede haber UNA plantilla activa por tipo de evento.
    """

    @abstractmethod
    def get_all_events(self) -> List[TemplateEvent]:
        """
        Obtiene todos los eventos con sus plantillas asignadas

        Returns:
            Lista de objetos TemplateEvent
        """
        pass

    @abstractmethod
    def get_event_by_type(self, event_type: str) -> Optional[TemplateEvent]:
        """
        Obtiene un evento específico por su tipo

        Args:
            event_type: Tipo de evento a buscar

        Returns:
            Objeto TemplateEvent o None si no existe
        """
        pass

    @abstractmethod
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
        pass

    @abstractmethod
    def check_template_in_use(self, template_name: str) -> bool:
        """
        Verifica si una plantilla está activa para algún evento

        Args:
            template_name: Nombre de la plantilla a verificar

        Returns:
            True si la plantilla está en uso, False en caso contrario
        """
        pass

    @abstractmethod
    def get_active_template_for_event(self, event_type: str) -> Optional[str]:
        """
        Obtiene el nombre de la plantilla activa para un evento

        Args:
            event_type: Tipo de evento

        Returns:
            Nombre de la plantilla activa o None
        """
        pass

    @abstractmethod
    def get_events_by_template(self, template_name: str) -> List[str]:
        """
        Obtiene los eventos que están asignados a una plantilla

        Args:
            template_name: Nombre de la plantilla

        Returns:
            Lista de tipos de eventos asignados a esta plantilla
        """
        pass
