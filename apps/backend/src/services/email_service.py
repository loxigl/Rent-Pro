import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from datetime import datetime
from jinja2 import Environment, FileSystemLoader, select_autoescape
import os

from src.config.settings import settings

logger = logging.getLogger(__name__)

# Инициализируем шаблонизатор для email-шаблонов
template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../templates/emails")
env = Environment(
    loader=FileSystemLoader(template_dir),
    autoescape=select_autoescape(['html', 'xml'])
)


async def send_email(recipient_email: str, subject: str, html_content: str, text_content: str = None):
    """
    Отправляет электронное письмо.
    
    Args:
        recipient_email: Email получателя.
        subject: Тема письма.
        html_content: HTML-содержимое письма.
        text_content: Текстовое содержимое письма (необязательно).
    """
    if not settings.SMTP_ENABLED:
        logger.info(f"SMTP отключен, письмо не отправлено. Тема: {subject}, Получатель: {recipient_email}")
        return False
    
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = settings.SMTP_FROM_EMAIL
        msg['To'] = recipient_email
        
        # Добавляем текстовую версию, если она предоставлена
        if text_content:
            text_part = MIMEText(text_content, 'plain', 'utf-8')
            msg.attach(text_part)
        
        # Добавляем HTML-версию
        html_part = MIMEText(html_content, 'html', 'utf-8')
        msg.attach(html_part)
        
        # Подключаемся к SMTP-серверу и отправляем письмо
        with smtplib.SMTP(settings.SMTP_SERVER, settings.SMTP_PORT) as server:
            if settings.SMTP_USE_TLS:
                server.starttls()
            
            if settings.SMTP_USERNAME and settings.SMTP_PASSWORD:
                server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            
            server.send_message(msg)
        
        logger.info(f"Письмо успешно отправлено: {subject} -> {recipient_email}")
        return True
    
    except Exception as e:
        logger.error(f"Ошибка при отправке письма: {str(e)}")
        return False


async def send_booking_created_notification(
    booking_id: int,
    client_name: str,
    client_email: str,
    client_phone: str,
    apartment_title: str,
    check_in_date: datetime,
    check_out_date: datetime,
    guests_count: int
):
    """
    Отправляет уведомление администратору о новом бронировании.
    """
    # Получаем шаблон
    template = env.get_template('admin_booking_notification.html')
    
    # Форматируем данные для шаблона
    html_content = template.render(
        booking_id=booking_id,
        client_name=client_name,
        client_email=client_email,
        client_phone=client_phone,
        apartment_title=apartment_title,
        check_in_date=check_in_date.strftime('%d.%m.%Y'),
        check_out_date=check_out_date.strftime('%d.%m.%Y'),
        guests_count=guests_count,
        admin_url=f"{settings.ADMIN_URL}/bookings",
        now=datetime.now
    )
    
    # Отправляем письмо администратору
    await send_email(
        recipient_email=settings.ADMIN_EMAIL,
        subject=f"Новое бронирование #{booking_id}",
        html_content=html_content
    )


async def send_booking_confirmation(
    booking_id: int,
    client_name: str,
    client_email: str,
    apartment_title: str,
    check_in_date: datetime,
    check_out_date: datetime,
    guests_count: int
):
    """
    Отправляет клиенту подтверждение бронирования.
    """
    # Получаем шаблон
    template = env.get_template('booking_confirmation.html')
    
    # Форматируем данные для шаблона
    html_content = template.render(
        booking_id=booking_id,
        client_name=client_name,
        apartment_title=apartment_title,
        check_in_date=check_in_date.strftime('%d.%m.%Y'),
        check_out_date=check_out_date.strftime('%d.%m.%Y'),
        guests_count=guests_count,
        support_email=settings.SUPPORT_EMAIL,
        support_phone=settings.SUPPORT_PHONE,
        site_url=settings.SITE_URL,
        now=datetime.now
    )
    
    # Отправляем письмо клиенту
    await send_email(
        recipient_email=client_email,
        subject=f"Подтверждение бронирования #{booking_id}",
        html_content=html_content
    )


async def send_booking_cancellation(
    booking_id: int,
    client_name: str,
    client_email: str,
    apartment_title: str,
    check_in_date: datetime,
    check_out_date: datetime
):
    """
    Отправляет клиенту уведомление об отмене бронирования.
    """
    # Получаем шаблон
    template = env.get_template('booking_cancellation.html')
    
    # Форматируем данные для шаблона
    html_content = template.render(
        booking_id=booking_id,
        client_name=client_name,
        apartment_title=apartment_title,
        check_in_date=check_in_date.strftime('%d.%m.%Y'),
        check_out_date=check_out_date.strftime('%d.%m.%Y'),
        support_email=settings.SUPPORT_EMAIL,
        support_phone=settings.SUPPORT_PHONE,
        site_url=settings.SITE_URL,
        now=datetime.now
    )
    
    # Отправляем письмо клиенту
    await send_email(
        recipient_email=client_email,
        subject=f"Отмена бронирования #{booking_id}",
        html_content=html_content
    ) 