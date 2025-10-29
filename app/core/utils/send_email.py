import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Union


def send_email(
    recipients: Union[str, List[str]],
    subject: str,
    html_body: str,
    smtp_server: str,
    smtp_port: int,
    smtp_user: str,
    smtp_password: str,
    sender_name: str = "Notificación Automática"
):
    """
    Envía un correo electrónico con cuerpo HTML a uno o varios destinatarios.

    Args:
        recipients (str | list[str]): Dirección o lista de direcciones de correo.
        subject (str): Asunto del correo.
        html_body (str): Contenido HTML del mensaje.
        smtp_server (str): Servidor SMTP (por ejemplo 'smtp.gmail.com').
        smtp_port (int): Puerto del servidor (587 TLS, 465 SSL).
        smtp_user (str): Usuario SMTP (correo del remitente).
        smtp_password (str): Contraseña o token del remitente.
        sender_name (str): Nombre que se mostrará como remitente.
    """
    if isinstance(recipients, str):
        recipients = [recipients]

    # Construir el mensaje
    msg = MIMEMultipart("alternative")
    msg["From"] = f"{sender_name} <{smtp_user}>"
    msg["To"] = ", ".join(recipients)
    msg["Subject"] = subject

    msg.attach(MIMEText(html_body, "html", "utf-8"))

    try:
        # Enviar usando TLS (puerto 587)
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
            print(f"✅ Correo enviado a: {', '.join(recipients)}")

    except smtplib.SMTPException as e:
        print(f"❌ Error al enviar el correo: {e}")
