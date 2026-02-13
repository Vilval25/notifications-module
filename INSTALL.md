# Guía de Instalación

## Paso 1: Instalar Dependencias

Abre una terminal en la carpeta del proyecto y ejecuta:

```bash
pip install -r requirements.txt
```

Esto instalará:
- `pybars3` - Motor de plantillas Handlebars
- `twilio` - Cliente para enviar SMS
- `requests` - Para llamadas HTTP (WhatsApp API)
- `python-dotenv` - Para cargar variables de entorno

## Paso 2: Configurar Variables de Entorno

1. Copia el archivo de ejemplo:
```bash
copy .env.example .env
```

2. Edita el archivo `.env` con tus credenciales reales:

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

### Importante para Gmail:
Si usas Gmail, necesitas crear una "App Password":
1. Ve a tu cuenta de Google
2. Seguridad → Verificación en dos pasos (activar si no está activo)
3. Contraseñas de aplicaciones
4. Genera una nueva contraseña para "Correo"
5. Usa esa contraseña en `SMTP_PASSWORD`

## Paso 3: Ejecutar el Ejemplo

```bash
python main.py
```

## Estructura de Archivos Importante

```
.env           ← Tu archivo con credenciales (NO subir a Git)
.env.example   ← Plantilla de ejemplo (SÍ subir a Git)
```

## Solución de Problemas

### Error: "Import dotenv could not be resolved"
- Asegúrate de haber ejecutado: `pip install -r requirements.txt`

### Error: "Template not found"
- Verifica que la carpeta `templates/` exista
- Verifica que `TEMPLATES_PATH=templates` esté en el `.env`

### Error al enviar email
- Verifica tus credenciales SMTP
- Si usas Gmail, necesitas una App Password
- Verifica que el puerto sea 587 para TLS

### Error de base de datos
- La base de datos SQLite se crea automáticamente
- Por defecto se crea `notifications.db` en la raíz del proyecto
