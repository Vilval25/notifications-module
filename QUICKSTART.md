# Guía Rápida de Inicio

Guía completa de instalación y uso del módulo de notificaciones.

---

## Instalación y Configuración

### 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

Esto instalará:
- `fastapi` - Framework web moderno
- `uvicorn` - Servidor ASGI
- `pydantic` - Validación de datos
- `pybars3` - Motor de plantillas Handlebars
- `twilio` - Cliente para enviar SMS
- `requests` - Para llamadas HTTP (WhatsApp API)
- `python-dotenv` - Para cargar variables de entorno

### 2. Configurar variables de entorno

**Copia el archivo de ejemplo:**
```bash
copy .env.example .env
```

**Edita `.env` con tus credenciales reales:**

```env
# Database
DB_PATH=notifications.db

# Templates
TEMPLATES_PATH=templates

# SMTP Configuration (Gmail ejemplo)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=tucorreo@gmail.com
SMTP_PASSWORD=tu_app_password
SMTP_FROM_EMAIL=tucorreo@gmail.com

# Twilio Configuration (opcional si no usas SMS)
TWILIO_ACCOUNT_SID=tu_account_sid
TWILIO_AUTH_TOKEN=tu_auth_token
TWILIO_FROM_PHONE=+1234567890

# WhatsApp Configuration (opcional si no usas WhatsApp)
WHATSAPP_API_TOKEN=tu_api_token
WHATSAPP_PHONE_ID=tu_phone_number_id
```

#### Importante para Gmail:
Si usas Gmail, necesitas crear una "App Password":
1. Ve a https://myaccount.google.com/security
2. Activa **Verificación en dos pasos**
3. Ve a **Contraseñas de aplicaciones**
4. Genera una nueva contraseña para "Correo"
5. Usa esa contraseña en `SMTP_PASSWORD` (NO tu contraseña normal)

---

## Uso

### Opción 1: API REST con FastAPI (Recomendado)

#### Iniciar el servidor

```bash
python app.py
```

Verás:
```
============================================================
🚀 Servidor de Notificaciones REST API con FastAPI
============================================================
Servidor iniciado en http://localhost:8000
📚 Documentación:
  • Swagger UI: http://localhost:8000/docs
  • ReDoc:      http://localhost:8000/redoc
============================================================
```

#### Explorar la documentación interactiva

Abre tu navegador en **http://localhost:8000/docs** para ver Swagger UI donde puedes:
- Ver todos los endpoints disponibles
- Probar la API directamente desde el navegador
- Ver los esquemas de request/response
- Descargar el esquema OpenAPI

#### Probar la API

**Opción A: Con Swagger UI (Recomendado)**
1. Abre http://localhost:8000/docs
2. Expande el endpoint `POST /api/notifications/send`
3. Click en **"Try it out"**
4. Edita el JSON de ejemplo
5. Click en **"Execute"**

**Opción B: Con curl**
```bash
curl -X POST http://localhost:8000/api/notifications/send \
  -H "Content-Type: application/json" \
  -d "{\"recipient\":\"tu_email@ejemplo.com\",\"channel\":\"email\",\"template_name\":\"welcome\",\"params\":{\"name\":\"Juan\",\"source_module\":\"TEST\"}}"
```

**Opción C: Con el script de prueba**
```bash
python test_api.py
```

**Opción D: Con Postman/Thunder Client**
- URL: `POST http://localhost:8000/api/notifications/send`
- Headers: `Content-Type: application/json`
- Body:
```json
{
  "recipient": "tu_email@ejemplo.com",
  "channel": "email",
  "template_name": "welcome",
  "params": {
    "name": "Tu Nombre",
    "source_module": "TEST"
  }
}
```

#### Endpoints Disponibles

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/` | Información de la API |
| GET | `/health` | Estado de salud |
| POST | `/api/notifications/send` | Enviar notificación |
| GET | `/api/notifications/logs` | Obtener logs |
| GET | `/docs` | Documentación Swagger UI |
| GET | `/redoc` | Documentación ReDoc |
| GET | `/openapi.json` | Esquema OpenAPI 3.0 |

---

### Opción 2: Como Librería Python

Si prefieres usar el módulo directamente en tu código Python:

```python
from dotenv import load_dotenv
load_dotenv()

from src.interface.notification_controller import NotificationController
from src.interface.notification_request import NotificationRequest
from src.domain.notification_channel import NotificationChannel
# ... (ver main.py para inicialización completa)

# Enviar notificación
request = NotificationRequest(
    recipient="usuario@ejemplo.com",
    channel=NotificationChannel.EMAIL,
    template_name="welcome",
    params={"name": "Juan", "source_module": "MI_APP"}
)

controller.send_notification(request)
```

**Ejecutar el ejemplo completo:**
```bash
python main.py
```

---

## Solución de Problemas

### Error: "Credenciales no configuradas"
- Asegúrate de tener el archivo `.env` en la raíz del proyecto
- Verifica que las variables estén configuradas correctamente

### Error: "Template not found"
- Verifica que existe `templates/welcome.hbs`
- Verifica que `TEMPLATES_PATH=templates` en `.env`

### Error de autenticación SMTP
- Si usas Gmail, necesitas una **App Password**, no tu contraseña normal
- Ve a https://myaccount.google.com/security
- Activa verificación en dos pasos
- Genera una "Contraseña de aplicación"

### Error: "Import dotenv could not be resolved"
- Ejecuta: `pip install -r requirements.txt`

### Error al enviar email
- Verifica tus credenciales SMTP
- Si usas Gmail, necesitas una App Password
- Verifica que el puerto sea 587 para TLS

### Error de base de datos
- La base de datos SQLite se crea automáticamente
- Por defecto se crea `notifications.db` en la raíz del proyecto

### Verificar configuración SMTP
```bash
python testing/test_smtp_config.py
```

---

## Más Información

- README completo: [README.md](README.md)
- Migración de Flask a FastAPI: [MIGRATION.md](MIGRATION.md)
- Ejemplos de testing: [testing/README.md](testing/README.md)
