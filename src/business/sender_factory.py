from ..domain.notification_channel import NotificationChannel
from ..infrastructure.senders.i_notification_sender import INotificationSender


class SenderFactory:
    """
    Fábrica para obtener el sender apropiado según el canal

    Acepta cualquier implementación de INotificationSender para cada canal,
    permitiendo usar implementaciones reales o mocks según sea necesario.
    """

    def __init__(self, smtp_sender: INotificationSender, sms_sender: INotificationSender,
                 whatsapp_sender: INotificationSender):
        """
        Inicializa la fábrica con los senders configurados

        Args:
            smtp_sender: Sender para email (SmtpSender)
            sms_sender: Sender para SMS (MockSmsSender)
            whatsapp_sender: Sender para WhatsApp (MockWhatsAppSender)
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
