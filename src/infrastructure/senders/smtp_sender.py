import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from .i_notification_sender import INotificationSender


class SmtpSender(INotificationSender):
    """Sender de notificaciones por email usando SMTP"""

    def __init__(self, host: str, port: int, username: str = None, password: str = None,
                 from_email: str = None, use_tls: bool = True):
        """
        Inicializa el sender SMTP

        Args:
            host: Host del servidor SMTP
            port: Puerto del servidor SMTP
            username: Usuario para autenticación (opcional)
            password: Contraseña para autenticación (opcional)
            from_email: Email del remitente
            use_tls: Si usar TLS para conexión segura
        """
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._from_email = from_email or username
        self._use_tls = use_tls

    def send(self, to: str, body: str) -> bool:
        """
        Envía un email

        Args:
            to: Email del destinatario
            body: Contenido del email (puede ser HTML)

        Returns:
            True si se envió correctamente, False en caso contrario
        """
        try:
            # Validar que tenemos las credenciales necesarias
            if not self._username or not self._password:
                print("❌ SMTP Error: Credenciales no configuradas")
                print(f"   Username: {'✓' if self._username else '✗'}")
                print(f"   Password: {'✓' if self._password else '✗'}")
                return False

            message = MIMEMultipart("alternative")
            message["Subject"] = "Notificación"
            message["From"] = self._from_email
            message["To"] = to

            html_part = MIMEText(body, "html")
            message.attach(html_part)

            print(f"📧 Intentando enviar email...")
            print(f"   Host: {self._host}:{self._port}")
            print(f"   From: {self._from_email}")
            print(f"   To: {to}")

            with smtplib.SMTP(self._host, self._port, timeout=10) as server:
                server.set_debuglevel(0)  # Cambiar a 1 para ver debug completo

                if self._use_tls:
                    print("   🔒 Iniciando TLS...")
                    server.starttls()

                print("   🔑 Autenticando...")
                server.login(self._username, self._password)

                print("   📤 Enviando mensaje...")
                server.send_message(message)

            print("   ✅ Email enviado exitosamente")
            return True

        except smtplib.SMTPAuthenticationError as e:
            print(f"❌ Error de autenticación SMTP: {e}")
            print("   Verifica tu username y password")
            print("   Si usas Gmail, necesitas una 'App Password'")
            return False
        except smtplib.SMTPException as e:
            print(f"❌ Error SMTP: {e}")
            return False
        except Exception as e:
            print(f"❌ Error inesperado enviando email: {type(e).__name__}: {e}")
            return False
