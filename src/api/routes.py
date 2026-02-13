"""
API REST para el módulo de notificaciones
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from ..domain.notification_channel import NotificationChannel
from ..interface.notification_request import NotificationRequest
from ..interface.notification_controller import NotificationController


def create_app(notification_controller: NotificationController) -> Flask:
    """
    Crea y configura la aplicación Flask

    Args:
        notification_controller: Controlador de notificaciones configurado

    Returns:
        Aplicación Flask configurada
    """
    app = Flask(__name__)
    CORS(app)

    @app.route('/', methods=['GET'])
    def home():
        """Endpoint de bienvenida"""
        return jsonify({
            "message": "API de Notificaciones",
            "version": "1.0",
            "endpoints": {
                "POST /api/notifications/send": "Enviar una notificación",
                "GET /api/notifications/logs": "Obtener logs de notificaciones",
                "GET /health": "Estado de la API"
            }
        })

    @app.route('/health', methods=['GET'])
    def health():
        """Endpoint de salud"""
        return jsonify({"status": "healthy"})

    @app.route('/api/notifications/send', methods=['POST'])
    def send_notification():
        """
        Envía una notificación

        Body JSON:
        {
            "recipient": "usuario@ejemplo.com",
            "channel": "email",
            "template_name": "welcome",
            "params": {
                "name": "Juan",
                "source_module": "TEST"
            }
        }
        """
        try:
            data = request.get_json()

            # Validar datos requeridos
            if not data:
                return jsonify({"error": "No se proporcionaron datos"}), 400

            required_fields = ['recipient', 'channel', 'template_name', 'params']
            for field in required_fields:
                if field not in data:
                    return jsonify({"error": f"Campo requerido: {field}"}), 400

            # Convertir canal a enum
            channel_map = {
                "email": NotificationChannel.EMAIL,
                "sms": NotificationChannel.SMS,
                "whatsapp": NotificationChannel.WHATSAPP
            }

            channel_str = data['channel'].lower()
            if channel_str not in channel_map:
                return jsonify({"error": f"Canal inválido: {channel_str}"}), 400

            channel = channel_map[channel_str]

            # Crear request de notificación
            notification_request = NotificationRequest(
                recipient=data['recipient'],
                channel=channel,
                template_name=data['template_name'],
                params=data['params']
            )

            # Enviar notificación
            result = notification_controller.send_notification(notification_request)

            return jsonify(result), 200 if result['status'] == 'success' else 500

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route('/api/notifications/logs', methods=['GET'])
    def get_logs():
        """
        Obtiene todos los logs de notificaciones

        Query params opcionales:
        - limit: número máximo de logs a devolver
        """
        try:
            limit = request.args.get('limit', type=int)

            logs = notification_controller.get_logs()

            # Convertir logs a diccionarios
            logs_dict = []
            for log in logs:
                logs_dict.append({
                    "id": log.id,
                    "recipient": log.recipient,
                    "channel": log.channel.value,
                    "content": log.content[:100] + "..." if len(log.content) > 100 else log.content,
                    "status": log.status,
                    "timestamp": log.timestamp.isoformat(),
                    "source_module": log.source_module
                })

            # Aplicar límite si se especificó
            if limit:
                logs_dict = logs_dict[:limit]

            return jsonify({
                "total": len(logs_dict),
                "logs": logs_dict
            }), 200

        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return app
