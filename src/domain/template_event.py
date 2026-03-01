"""
Entidad de dominio para eventos de plantillas
"""

from dataclasses import dataclass
from datetime import datetime


@dataclass
class TemplateEvent:
    """
    Entidad que representa la asignación de una plantilla a un evento del sistema

    Attributes:
        id: Identificador único
        event_type: Tipo de evento (tramite_observado, tramite_aprobado, etc.)
        template_name: Nombre de la plantilla asignada (sin extensión .hbs)
        is_active: Si esta plantilla está activa para el evento
        created_at: Fecha de creación del registro
        updated_at: Fecha de última actualización
    """
    id: int
    event_type: str
    template_name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
