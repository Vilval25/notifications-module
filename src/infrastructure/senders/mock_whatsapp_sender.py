"""
Mock WhatsApp Sender - Simula el envío de WhatsApp sin enviar realmente
"""
from .i_notification_sender import INotificationSender
import time


class MockWhatsAppSender(INotificationSender):
    """
    Sender mock de WhatsApp para desarrollo y testing

    Simula el envío de mensajes de WhatsApp sin conectarse a Meta Business API.
    Útil para desarrollo local y pruebas sin necesitar credenciales reales.
    """

    def __init__(self, api_token: str = "mock_token", phone_number_id: str = "mock_phone_id"):
        """
        Inicializa el sender mock de WhatsApp

        Args:
            api_token: Token simulado de Meta API (no se usa)
            phone_number_id: ID simulado del número de WhatsApp Business (no se usa)
        """
        self._api_token = api_token
        self._phone_number_id = phone_number_id
        self._sent_messages = []  # Guarda los mensajes "enviados" para inspección

    def send(self, to: str, body: str) -> bool:
        """
        Simula el envío de un mensaje por WhatsApp

        Args:
            to: Número de teléfono del destinatario (formato: +[código país][número])
            body: Contenido del mensaje

        Returns:
            True (siempre exitoso en modo mock)
        """
        try:
            # Simular un pequeño delay como si fuera una llamada a API real
            time.sleep(0.15)

            # Guardar mensaje simulado
            message_data = {
                "to": to,
                "body": body,
                "status": "sent",
                "message_id": f"mock_wa_{len(self._sent_messages) + 1}",
                "phone_number_id": self._phone_number_id
            }
            self._sent_messages.append(message_data)

            # Log del mensaje simulado
            print(f"\n[MOCK WhatsApp] Mensaje simulado enviado:")
            print(f"   Para: {to}")
            print(f"   Phone ID: {self._phone_number_id}")
            print(f"   Contenido: {body[:50]}{'...' if len(body) > 50 else ''}")
            print(f"   Status: SENT (simulated)")

            return True

        except Exception as e:
            print(f"[MOCK WhatsApp] Error en simulacion: {e}")
            return False

    def get_sent_messages(self):
        """
        Obtiene todos los mensajes simulados enviados

        Útil para testing y verificación

        Returns:
            Lista de mensajes simulados
        """
        return self._sent_messages

    def clear_history(self):
        """Limpia el historial de mensajes simulados"""
        self._sent_messages = []
