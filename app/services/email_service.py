import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Union
from jinja2 import Environment, FileSystemLoader, select_autoescape
from app.core.config import settings


class EmailService:
    """
    Servicio para envío de correos HTML a través de Gmail.
    Incluye renderizado dinámico de plantillas Jinja2.
    """

    TEMPLATE_PATH = "templates"

    @staticmethod
    def _render_template(template_name: str, context: dict) -> str:
        """
        Renderiza un template HTML con el contexto proporcionado.
        """
        env = Environment(
            loader=FileSystemLoader(EmailService.TEMPLATE_PATH),
            autoescape=select_autoescape(["html", "xml"])
        )
        template = env.get_template(template_name)
        context["anio_actual"] = datetime.now().year
        return template.render(context)

    @staticmethod
    def send_email(
        recipients: Union[str, List[str]],
        subject: str,
        html_body: str
    ):
        """
        Envía un correo electrónico con cuerpo HTML.
        """
        if isinstance(recipients, str):
            recipients = [recipients]

        msg = MIMEMultipart("alternative")
        msg["From"] = f"{settings.EMAIL_SENDER_NAME} <{settings.SMTP_USER}>"
        msg["To"] = ", ".join(recipients)
        msg["Subject"] = subject

        msg.attach(MIMEText(html_body, "html", "utf-8"))

        try:
            with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)

            print(f"✅ Correo enviado a: {', '.join(recipients)}")

        except smtplib.SMTPException as e:
            print(f"❌ Error al enviar correo: {e}")
            raise e

    @staticmethod
    def send_benefit_notification(
        recipient_email: str,
        context: dict
    ):
        """
        Envía el correo de notificación de canje de beneficio.
        Parámetros esperados en 'context':
          - nombre_colaborador
          - nombre_beneficio
          - imagen_beneficio
          - detalle_beneficio
          - puntos_utilizados
          - puntos_restantes
          - fecha_canje
          - fecha_uso
          - jornada (opcional)
          - comentarios (opcional)
        """
        subject = f"Confirmación de Canje: {context.get('nombre_beneficio', '')}"
        html_body = EmailService._render_template("email_beneficio.html", context)
        EmailService.send_email(recipient_email, subject, html_body)
