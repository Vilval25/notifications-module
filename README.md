# Módulo de Notificaciones

Sistema de notificaciones multi-canal con arquitectura por capas basado en Clean Architecture, sistema de eventos de negocio y notificaciones internas para usuarios.

## Estructura del Proyecto

```
Modulo de Notificaciones/
│
├── src/
│   ├── domain/                      # Capa de Dominio
│   │   ├── notification_channel.py  # Enum de canales
│   │   └── notification_log.py      # Entidad de log
│   │
│   ├── interface/                   # Capa de Interfaz
│   │   ├── notification_request.py  # DTO de request
│   │   └── notification_controller.py # Controlador
│   │
│   ├── business/                    # Capa de Negocio
│   │   ├── i_template_engine.py     # Interface template engine
│   │   ├── handlebars_engine.py     # Implementación Handlebars
│   │   ├── sender_factory.py        # Factory de senders
│   │   ├── notification_service.py  # Servicio principal
│   │   └── event_notification_service.py # Servicio de eventos unificados
│   │
│   ├── infrastructure/              # Capa de Infraestructura
│   │   ├── senders/
│   │   │   ├── i_notification_sender.py    # Interface sender
│   │   │   ├── smtp_sender.py              # Sender Email
│   │   │   ├── mock_sms_sender.py          # Sender SMS (Mock)
│   │   │   └── mock_whatsapp_sender.py     # Sender WhatsApp (Mock)
│   │   │
│   │   └── repository/
│   │       ├── i_notification_log_repository.py        # Interface logs de notificaciones
│   │       ├── sql_notification_log_repository.py      # Implementación SQL logs
│   │       ├── i_internal_notification_repository.py   # Interface notificaciones internas
│   │       ├── internal_notification_repository.py     # Implementación notificaciones internas
│   │       ├── i_subscription_repository.py            # Interface preferencias usuario
│   │       ├── subscription_repository.py              # Implementación preferencias
│   │       ├── i_template_event_repository.py          # Interface eventos plantillas
│   │       └── template_event_repository.py            # Implementación eventos plantillas
│   │
│   └── api/                         # Capa de API REST
│       ├── __init__.py
│       ├── routes.py                        # Endpoints generales
│       ├── models.py                        # Modelos generales
│       ├── event_notification_routes.py     # Endpoints de eventos unificados
│       ├── event_notification_models.py     # Modelos de eventos unificados
│       ├── internal_notification_routes.py  # Endpoints notificaciones internas
│       ├── internal_notification_models.py  # Modelos notificaciones internas
│       ├── subscription_routes.py           # Endpoints preferencias usuario
│       ├── subscription_models.py           # Modelos preferencias
│       └── template_models.py               # Modelos de plantillas
│
├── config/                          # Configuración
│   └── config.py
│
├── templates/                       # Plantillas Handlebars de eventos
│   ├── tramite_registrado.hbs
│   ├── tramite_observado.hbs
│   ├── tramite_aprobado.hbs
│   ├── tramite_rechazado.hbs
│   ├── creacion_cuenta.hbs
│   ├── cambio_contrasena.hbs
│   └── comprobante_pago.hbs
│
├── static/                          # Archivos estáticos del frontend
│   ├── css/                         # Estilos
│   ├── js/                          # JavaScript
│   ├── templates.html               # UI de gestión de plantillas
│   └── notifications.html           # UI de notificaciones de usuario
│
├── app.py                           # 🚀 Servidor REST API principal
├── main.py                          # Ejemplo de uso como librería
├── requirements.txt                 # Dependencias
└── .env.example                     # Ejemplo de variables de entorno

```

## Características

- **Arquitectura por Capas**: Separación clara entre dominio, negocio, interfaz, infraestructura y API
- **Sistema de Eventos**: Notificaciones basadas en eventos de negocio con plantillas activas
- **Notificaciones Internas**: Panel de usuario para historial de notificaciones de trámites
- **Gestión de Plantillas**: UI web para CRUD completo de plantillas Handlebars
- **FastAPI + OpenAPI**: API REST moderna con documentación automática Swagger/ReDoc
- **Validación Automática**: Pydantic para validación de requests/responses
- **Multi-canal**: Soporte para Email (SMTP), SMS (simulado) y WhatsApp (simulado)
- **Motor de Plantillas**: Uso de Handlebars para personalizar mensajes
- **Persistencia SQL Nativa**: Implementación directa con SQL usando SQLite (fácilmente adaptable a PostgreSQL/MySQL)
- **Factory Pattern**: Selección dinámica del canal de envío
- **Logging**: Registro completo de todas las notificaciones enviadas
- **Dual Mode**: Usar como API REST o como librería Python

## Instalación Rápida

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Configurar variables de entorno
copy .env.example .env
# Edita .env con tus credenciales

# 3. Iniciar servidor
python app.py
```

## Uso

### Opción 1: Como API REST con FastAPI (Recomendado)

#### Iniciar el servidor:
```bash
python app.py
```

El servidor se iniciará en `http://localhost:8000`

#### Ver documentación interactiva:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI Schema**: http://localhost:8000/openapi.json

Desde Swagger UI puedes probar todos los endpoints directamente desde el navegador!

#### Gestión de Plantillas (UI Web):
```
http://localhost:8000/templates-ui
```

Interfaz web para:
- Crear, editar y eliminar plantillas
- Activar/desactivar plantillas por evento
- Editor WYSIWYG con Quill.js
- Gestión de eventos de negocio

#### Enviar notificaciones vía API (Endpoints de Eventos Unificados):

**1. Evento de Trámite** (crea notificación interna + envío multicanal):
```bash
curl -X POST http://localhost:8000/api/events/tramite \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user_demo",
    "user_email": "juan.perez@ejemplo.com",
    "user_name": "Juan Pérez",
    "user_phone": "+51999888777",
    "solicitud_id": "SOL-2024-001",
    "event_type": "tramite_aprobado",
    "solicitud_subject": "Solicitud de Certificado de Estudios",
    "solicitud_url": "https://campus360.com/tramites/SOL-2024-001",
    "source_module": "TRAMITES"
  }'
```

**2. Evento de Creación de Cuenta** (solo email):
```bash
curl -X POST http://localhost:8000/api/events/creacion-cuenta \
  -H "Content-Type: application/json" \
  -d '{
    "user_email": "maria.garcia@ejemplo.com",
    "user_name": "María García",
    "activation_url": "https://campus360.com/activate/abc123",
    "temporary_password": "Temp1234",
    "source_module": "USER_REGISTRATION"
  }'
```

**3. Evento de Cambio de Contraseña** (solo email):
```bash
curl -X POST http://localhost:8000/api/events/cambio-contrasena \
  -H "Content-Type: application/json" \
  -d '{
    "user_email": "carlos.lopez@ejemplo.com",
    "user_name": "Carlos López",
    "reset_url": "https://campus360.com/reset-password/xyz789",
    "reset_code": "123456",
    "source_module": "AUTH"
  }'
```

**4. Evento de Comprobante de Pago** (solo email):
```bash
curl -X POST http://localhost:8000/api/events/comprobante-pago \
  -H "Content-Type: application/json" \
  -d '{
    "user_email": "estudiante@ejemplo.com",
    "user_name": "María López",
    "enlace": "https://campus360.com/pagos/comprobante/abc123",
    "telefono": "+51999888777",
    "source_module": "PAGOS"
  }'
```

**Eventos de Trámites disponibles:**
- `tramite_registrado` - Trámite registrado
- `tramite_observado` - Trámite con observaciones
- `tramite_aprobado` - Trámite aprobado
- `tramite_rechazado` - Trámite rechazado

#### Ver logs vía API:
```bash
curl http://localhost:8000/api/notifications/logs?limit=10
```

#### Endpoints disponibles:

**Generales:**
- `GET /` - Información de la API
- `GET /health` - Estado de salud del servidor
- `GET /docs` - Documentación Swagger UI (interactiva) 🔥
- `GET /redoc` - Documentación ReDoc (alternativa)

**🎯 Eventos Unificados (Para Módulos Externos):**
- `POST /api/events/tramite` - Procesar evento de trámite (crea notif interna + multicanal)
- `POST /api/events/creacion-cuenta` - Procesar creación de cuenta (solo email)
- `POST /api/events/cambio-contrasena` - Procesar cambio de contraseña (solo email)
- `POST /api/events/comprobante-pago` - Procesar comprobante de pago (solo email)

**📋 Notificaciones Internas:**
- `GET /user-notifications` - Panel web de notificaciones del usuario 🔥
- `GET /api/internal-notifications/user/{user_id}` - Obtener notificaciones de usuario
- `GET /api/internal-notifications/user/{user_id}/summary` - Resumen de notificaciones
- `GET /api/internal-notifications/user/{user_id}/unread-count` - Contador de no leídas
- `POST /api/internal-notifications` - Crear notificación interna manualmente
- `PUT /api/internal-notifications/{id}/read` - Marcar como leída
- `PUT /api/internal-notifications/user/{user_id}/read-all` - Marcar todas como leídas
- `DELETE /api/internal-notifications/{id}` - Eliminar notificación

**⚙️ Preferencias de Usuario:**
- `GET /api/subscriptions/user/{user_id}` - Obtener preferencias de notificación
- `POST /api/subscriptions/user/{user_id}` - Guardar/actualizar preferencias

**📝 Gestión de Plantillas:**
- `GET /templates-ui` - Interfaz web de gestión de plantillas 🔥
- `GET /api/templates` - Listar todas las plantillas
- `GET /api/templates/{id}` - Obtener una plantilla específica
- `POST /api/templates` - Crear nueva plantilla
- `PUT /api/templates/{id}` - Actualizar plantilla existente
- `DELETE /api/templates/{id}` - Eliminar plantilla
- `GET /api/templates/event/{event_type}/active` - Obtener plantilla activa por evento
- `PUT /api/templates/{id}/activate` - Activar plantilla para un evento

**📊 Logs y Monitoreo:**
- `GET /api/notifications/logs` - Obtener logs de notificaciones enviadas

### Opción 2: Como librería Python

```python
from src.interface.notification_controller import NotificationController
from src.interface.notification_request import NotificationRequest
from src.domain.notification_channel import NotificationChannel

# Inicializar el controlador (ver main.py para configuración completa)
controller = initialize_app()

# Enviar notificación por email
request = NotificationRequest(
    recipient="usuario@ejemplo.com",
    channel=NotificationChannel.EMAIL,
    template_name="tramite_aprobado",
    params={
        "nombre": "Juan Pérez",
        "email": "usuario@ejemplo.com",
        "enlace": "https://campus360.com/tramite/123",
        "telefono": "+51 999 999 999",
        "source_module": "TRAMITES"
    }
)

result = controller.send_notification(request)
print(result)
```

### Ejecutar el ejemplo

```bash
python main.py
```

## Sistema de Notificaciones Internas

El módulo incluye un sistema de notificaciones internas que permite mostrar un historial de eventos de trámites en el panel de usuario.

### Características del Panel de Usuario

- ✅ Tabla de notificaciones con estado (leída/no leída)
- ✅ Filtros por estado y tipo de evento
- ✅ Búsqueda por ID de solicitud o asunto
- ✅ Contador de notificaciones no leídas
- ✅ Enlace directo a cada solicitud
- ✅ Auto-refresh cada 30 segundos

### Acceder al Panel

```
http://localhost:8000/user-notifications
```

### Crear Notificación Interna

```bash
curl -X POST http://localhost:8000/api/internal-notifications \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "solicitud_id": "SOL-2024-001",
    "event_type": "tramite_aprobado",
    "notification_subject": "Trámite aprobado",
    "solicitud_subject": "Solicitud de certificado de estudios",
    "solicitud_url": "https://campus360.com/tramites/SOL-2024-001"
  }'
```

**Eventos de Trámites:**
- `tramite_registrado` - Trámite registrado
- `tramite_observado` - Trámite observado
- `tramite_aprobado` - Trámite aprobado
- `tramite_rechazado` - Trámite rechazado

## Configuración

### SMTP (Email)
- `SMTP_HOST`: Host del servidor SMTP
- `SMTP_PORT`: Puerto (generalmente 587)
- `SMTP_USERNAME`: Usuario de email
- `SMTP_PASSWORD`: Contraseña o app password
- `SMTP_FROM_EMAIL`: Email del remitente

## Notificaciones SMS y WhatsApp

El sistema incluye senders mock para SMS y WhatsApp que **simulan** el envío sin conectarse a servicios externos:
- ✅ Útil para desarrollo y testing
- ✅ No requiere credenciales de APIs externas
- ✅ Muestra mensajes en consola con formato ASCII
- ✅ Guarda historial en logs de base de datos

Para integrar servicios reales (Twilio, WhatsApp Business API), solo necesitas implementar la interfaz `INotificationSender` en `src/infrastructure/senders/` y registrar el nuevo sender en `SenderFactory`.

## Base de Datos

El repositorio utiliza SQL nativo con SQLite por defecto. La tabla se crea automáticamente:

```sql
CREATE TABLE notification_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    recipient TEXT NOT NULL,
    channel TEXT NOT NULL,
    content TEXT NOT NULL,
    status TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    source_module TEXT NOT NULL
)
```

Para usar PostgreSQL o MySQL, solo necesitas modificar `SqlNotificationLogRepository` para usar el conector apropiado (psycopg2, mysql-connector, etc).

## Plantillas

Las plantillas usan sintaxis Handlebars (.hbs):

```handlebars
<h1>¡Bienvenido {{name}}!</h1>
<p>{{message}}</p>
```

## Arquitectura

El proyecto sigue el patrón de **Clean Architecture**:

1. **Capa de Dominio**: Entidades y enums del negocio
2. **Capa de Interfaz**: Controllers y DTOs
3. **Capa de Negocio**: Servicios y lógica de negocio
4. **Capa de Infraestructura**: Implementaciones concretas (senders, repository)

## Diagrama de Clases

El proyecto implementa el diagrama UML proporcionado con énfasis en:
- Implementación SQL nativa en el repositorio
- Factory pattern para senders
- Interfaces para extensibilidad
- Separación de responsabilidades

## Licencia

MIT
