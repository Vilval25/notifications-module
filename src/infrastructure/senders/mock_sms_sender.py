"""
Mock SMS Sender - Simula el envío de SMS sin enviar realmente
"""
from .i_notification_sender import INotificationSender
import time


class MockSmsSender(INotificationSender):
    """
    Sender mock de SMS para desarrollo y testing

    Simula el envío de SMS sin conectarse a ningún servicio real.
    Útil para desarrollo local y pruebas sin consumir créditos de Twilio.
    """

    def __init__(self, account_sid: str = "mock_sid", auth_token: str = "mock_token",
                 from_phone: str = "+1234567890"):
        """
        Inicializa el sender mock de SMS

        Args:
            account_sid: SID simulado (no se usa)
            auth_token: Token simulado (no se usa)
            from_phone: Número de teléfono origen simulado
        """
        self._account_sid = account_sid
        self._auth_token = auth_token
        self._from_phone = from_phone
        self._sent_messages = []  # Guarda los mensajes "enviados" para inspección

    def send(self, to: str, body: str) -> bool:
        """
        Simula el envío de un SMS

        Args:
            to: Número de teléfono del destinatario
            body: Contenido del SMS

        Returns:
            True (siempre exitoso en modo mock)
        """
        try:
            # Simular un pequeño delay como si fuera una llamada a API real
            time.sleep(0.1)

            # Guardar mensaje simulado
            message_data = {
                "to": to,
                "from": self._from_phone,
                "body": body,
                "status": "sent",
                "sid": f"mock_sms_{len(self._sent_messages) + 1}"
            }
            self._sent_messages.append(message_data)

            # Log del mensaje simulado
            print(f"\n[MOCK SMS] Mensaje simulado enviado:")
            print(f"   De: {self._from_phone}")
            print(f"   Para: {to}")
            print(f"   Contenido: {body[:50]}{'...' if len(body) > 50 else ''}")
            print(f"   Status: SENT (simulated)")

            return True

        except Exception as e:
            print(f"[MOCK SMS] Error en simulacion: {e}")
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
