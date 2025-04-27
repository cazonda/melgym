import os
from io import BytesIO
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from weasyprint import HTML
import logging

logger = logging.getLogger(__name__)

def render_pdf_template(context, template_name):
    """Renderiza template para PDF usando WeasyPrint"""
    try:
        html_content = render_to_string(
            f'membership/pdf/{template_name}',
            context
        )
        pdf_file = HTML(string=html_content, base_url=settings.BASE_DIR).write_pdf()
        return pdf_file
    except Exception as e:
        logger.error(f"Erro ao gerar PDF: {str(e)}", exc_info=True)
        raise

def send_payment_confirmation_email(member_membership):
    """
    Envia email de confirmação com recibo PDF anexado
    
    Args:
        member_membership: Instância de MemberMembership
        
    Returns:
        tuple: (success: bool, message: str)
    """
    try:
        # Contexto para os templates
        context = {
            'member': member_membership.member,
            'membership': member_membership,
            'invoice_number': member_membership.id,
            'company': {
                'name': settings.COMPANY_NAME,
                'address': settings.COMPANY_ADDRESS,
                'phone': settings.COMPANY_PHONE,
                'email': settings.COMPANY_EMAIL,
            }
        }

        # 1. Gerar PDF
        pdf_content = render_pdf_template(context, 'invoice_template.html')

        # 2. Preparar email
        subject = f'Confirmação de Pagamento - Recibo #{member_membership.id}'
        html_message = render_to_string(
            'membership/emails/payment_confirmation.html',
            context
        )
        plain_message = strip_tags(html_message)

        # 3. Criar e enviar email
        email = EmailMessage(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [member_membership.member.email],
            reply_to=[settings.COMPANY_EMAIL],
        )
        email.content_subtype = "html"
        email.attach(
            f'Recibo_{member_membership.id}.pdf',
            pdf_content,
            'application/pdf'
        )
        
        email.send()
        return True, "Email enviado com sucesso"

    except Exception as e:
        logger.error(f"Erro ao enviar email: {str(e)}", exc_info=True)
        return False, str(e)