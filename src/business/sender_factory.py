from ..domain.notification_channel import NotificationChannel
from ..infrastructure.senders.i_notification_sender import INotificationSender
from ..infrastructure.senders.smtp_sender import SmtpSender
from ..infrastructure.senders.twilio_sms_sender import TwilioSmsSender
from ..infrastructure.senders.meta_whatsapp_sender import MetaWhatsAppSender


class SenderFactory:
    """Fábrica para obtener el sender apropiado según el canal"""

    def __init__(self, smtp_sender: SmtpSender, sms_sender: TwilioSmsSender,
                 whatsapp_sender: MetaWhatsAppSender):
        """
        Inicializa la fábrica con los senders configurados

        Args:
            smtp_sender: Sender para email
            sms_sender: Sender para SMS
            whatsapp_sender: Sender para WhatsApp
        """
        self._senders = {
            NotificationChannel.EMAIL: smtp_sender,
            NotificationChannel.SMS: sms_sender,
            NotificationChannel.WHATSAPP: whatsapp_sender
        }

    def get_sender(self, channel: NotificationChannel) -> INotificationSender:
        """
        Obtiene el sender apropiado para el canal especificado

        Args:
            channel: Canal de notificación

        Returns:
            Instancia del sender apropiado

        Raises:
            ValueError: Si el canal no está soportado
        """
        sender = self._senders.get(channel)
        if sender is None:
            raise ValueError(f"Channel not supported: {channel}")
        return sender
