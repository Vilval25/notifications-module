# Guía Rápida de Inicio

## 🚀 Inicio Rápido (5 minutos)

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Configurar credenciales

Copia el archivo de ejemplo:
```bash
copy .env.example .env
```

Edita `.env` con tus credenciales (mínimo SMTP para email):
```env
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=tu_email@gmail.com
SMTP_PASSWORD=tu_app_password
SMTP_FROM_EMAIL=tu_email@gmail.com
```

**Para Gmail:** Necesitas generar una "Contraseña de aplicación" en https://myaccount.google.com/security

### 3. Iniciar el servidor
```bash
python app.py
```

Verás:
```
============================================================
🚀 Servidor de Notificaciones REST API
============================================================
Servidor iniciado en http://localhost:5000
============================================================
```

### 4. Probar la API

**Opción A: Con curl**
```bash
curl -X POST http://localhost:5000/api/notifications/send \
  -H "Content-Type: application/json" \
  -d "{\"recipient\":\"tu_email@ejemplo.com\",\"channel\":\"email\",\"template_name\":\"welcome\",\"params\":{\"name\":\"Juan\",\"source_module\":\"TEST\"}}"
```

**Opción B: Con el script de prueba**
```bash
python test_api.py
```

**Opción C: Con Postman/Thunder Client**
- URL: `POST http://localhost:5000/api/notifications/send`
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

## 📋 Endpoints Disponibles

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/` | Información de la API |
| GET | `/health` | Estado de salud |
| POST | `/api/notifications/send` | Enviar notificación |
| GET | `/api/notifications/logs` | Obtener logs |

## 🔧 Uso como Librería Python

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

## 🛠 Solución de Problemas

### Error: "Credenciales no configuradas"
- Asegúrate de tener el archivo `.env` en la raíz del proyecto
- Verifica que las variables estén configuradas correctamente

### Error: "Template not found"
- Verifica que existe `templates/welcome.hbs`
- Verifica que `TEMPLATES_PATH=templates` en `.env`

### Error de autenticación SMTP
- Si usas Gmail, necesitas una "App Password", no tu contraseña normal
- Ve a https://myaccount.google.com/security
- Activa verificación en dos pasos
- Genera una "Contraseña de aplicación"

### Verificar configuración SMTP
```bash
python testing/test_smtp_config.py
```

## 📚 Más Información

- README completo: [README.md](README.md)
- Guía de instalación: [INSTALL.md](INSTALL.md)
- Ejemplos de testing: [testing/README.md](testing/README.md)
