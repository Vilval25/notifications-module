from .i_notification_sender import INotificationSender


class TwilioSmsSender(INotificationSender):
    """Sender de notificaciones por SMS usando Twilio"""

    def __init__(self, account_sid: str, auth_token: str, from_phone: str):
        """
        Inicializa el sender de Twilio

        Args:
            account_sid: SID de la cuenta de Twilio
            auth_token: Token de autenticación
            from_phone: Número de teléfono origen
        """
        self._account_sid = account_sid
        self._auth_token = auth_token
        self._from_phone = from_phone

    def send(self, to: str, body: str) -> bool:
        """
        Envía un SMS usando Twilio

        Args:
            to: Número de teléfono del destinatario
            body: Contenido del SMS

        Returns:
            True si se envió correctamente, False en caso contrario
        """
        try:
            from twilio.rest import Client

            client = Client(self._account_sid, self._auth_token)

            message = client.messages.create(
                body=body,
                from_=self._from_phone,
                to=to
            )

            return message.sid is not None
        except Exception as e:
            print(f"Error sending SMS: {e}")
            return False
