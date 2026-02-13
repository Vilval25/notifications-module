import requests
from .i_notification_sender import INotificationSender


class MetaWhatsAppSender(INotificationSender):
    """Sender de notificaciones por WhatsApp usando Meta Business API"""

    def __init__(self, api_token: str, phone_number_id: str):
        """
        Inicializa el sender de WhatsApp

        Args:
            api_token: Token de acceso de la API de Meta
            phone_number_id: ID del número de teléfono de WhatsApp Business
        """
        self._api_token = api_token
        self._phone_number_id = phone_number_id
        self._api_url = f"https://graph.facebook.com/v18.0/{phone_number_id}/messages"

    def send(self, to: str, body: str) -> bool:
        """
        Envía un mensaje por WhatsApp usando Meta Business API

        Args:
            to: Número de teléfono del destinatario (formato: +[código país][número])
            body: Contenido del mensaje

        Returns:
            True si se envió correctamente, False en caso contrario
        """
        try:
            headers = {
                "Authorization": f"Bearer {self._api_token}",
                "Content-Type": "application/json"
            }

            payload = {
                "messaging_product": "whatsapp",
                "to": to,
                "type": "text",
                "text": {
                    "body": body
                }
            }

            response = requests.post(self._api_url, json=payload, headers=headers)

            return response.status_code == 200
        except Exception as e:
            print(f"Error sending WhatsApp message: {e}")
            return False
