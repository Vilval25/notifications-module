# Módulo de Notificaciones

Sistema de notificaciones multi-canal con arquitectura por capas basado en Clean Architecture.

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
│   │   └── notification_service.py  # Servicio principal
│   │
│   ├── infrastructure/              # Capa de Infraestructura
│   │   ├── senders/
│   │   │   ├── i_notification_sender.py    # Interface sender
│   │   │   ├── smtp_sender.py              # Sender Email
│   │   │   ├── twilio_sms_sender.py        # Sender SMS
│   │   │   └── meta_whatsapp_sender.py     # Sender WhatsApp
│   │   │
│   │   └── repository/
│   │       ├── i_notification_repository.py     # Interface repositorio
│   │       └── sql_notification_repository.py   # Implementación SQL nativa
│   │
│   └── api/                         # Capa de API REST
│       ├── __init__.py
│       └── routes.py                # Endpoints REST
│
├── config/                          # Configuración
│   └── config.py
│
├── templates/                       # Plantillas Handlebars
│   ├── welcome.hbs
│   └── notification.hbs
│
├── testing/                         # Pruebas y scripts de testing
│   ├── endpoints.py                 # (Deprecado: usar app.py)
│   ├── test_requests.py             # Script de pruebas
│   ├── test_smtp_config.py          # Diagnóstico SMTP
│   └── requirements.txt             # (Deprecado: ahora en raíz)
│
├── app.py                           # 🚀 Servidor REST API principal
├── main.py                          # Ejemplo de uso como librería
├── requirements.txt                 # Dependencias
└── .env.example                     # Ejemplo de variables de entorno

```

## Características

- **Arquitectura por Capas**: Separación clara entre dominio, negocio, interfaz, infraestructura y API
- **FastAPI + OpenAPI**: API REST moderna con documentación automática Swagger/ReDoc
- **Validación Automática**: Pydantic para validación de requests/responses
- **Multi-canal**: Soporte para Email (SMTP), SMS (Twilio) y WhatsApp (Meta Business API)
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

**Ver guía completa:** [QUICKSTART.md](QUICKSTART.md)

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

#### Enviar notificación vía API:
```bash
curl -X POST http://localhost:8000/api/notifications/send \
  -H "Content-Type: application/json" \
  -d '{
    "recipient": "usuario@ejemplo.com",
    "channel": "email",
    "template_name": "welcome",
    "params": {
      "name": "Juan Pérez",
      "source_module": "USER_REGISTRATION"
    }
  }'
```

#### Ver logs vía API:
```bash
curl http://localhost:8000/api/notifications/logs?limit=10
```

#### Endpoints disponibles:
- `GET /` - Información de la API
- `GET /health` - Estado de salud
- `POST /api/notifications/send` - Enviar notificación
- `GET /api/notifications/logs` - Obtener logs
- `GET /docs` - Documentación Swagger UI (interactiva)
- `GET /redoc` - Documentación ReDoc (alternativa)

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
    template_name="welcome",
    params={
        "name": "Juan Pérez",
        "source_module": "USER_REGISTRATION"
    }
)

result = controller.send_notification(request)
print(result)
```

### Ejecutar el ejemplo

```bash
python main.py
```

## Configuración

### SMTP (Email)
- `SMTP_HOST`: Host del servidor SMTP
- `SMTP_PORT`: Puerto (generalmente 587)
- `SMTP_USERNAME`: Usuario de email
- `SMTP_PASSWORD`: Contraseña o app password
- `SMTP_FROM_EMAIL`: Email del remitente

### Twilio (SMS)
- `TWILIO_ACCOUNT_SID`: SID de cuenta Twilio
- `TWILIO_AUTH_TOKEN`: Token de autenticación
- `TWILIO_FROM_PHONE`: Número de teléfono origen

### WhatsApp (Meta Business API)
- `WHATSAPP_API_TOKEN`: Token de acceso de Meta
- `WHATSAPP_PHONE_ID`: ID del número de WhatsApp Business

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

Para usar PostgreSQL o MySQL, solo necesitas modificar `SqlNotificationRepository` para usar el conector apropiado (psycopg2, mysql-connector, etc).

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
