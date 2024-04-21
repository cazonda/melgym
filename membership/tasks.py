from datetime import timedelta
from django.utils import timezone
from celery import shared_task
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail

from membership.models import MemberMembership, Preferences

@shared_task(bind=True)
def send_subscription_expire_func(self):
    expired_memberships = MemberMembership.objects.filter(expiry_date__lt=timezone.now())

    for membership in expired_memberships:
        member = membership.member
        send_email(
            member=member, 
            messageType='SUBSCRIPTION_EXPIRATION',
            subjectProp='Subscrição Expirada',
            messageProp=f'Olá {member.first_name},\n\nSua subscrição expirou. Por favor, renove sua subscrição para continuar acessando nossos serviços.\n\nAtenciosamente,\n\nA equipe da Melgym')
        
    return 'done'

@shared_task(bind=True)
def send_subscription_warning_func(self):
    expiration_date_threshold = timezone.now() + timedelta(days=10)
    memberships_to_expire_soon = MemberMembership.objects.filter(expiry_date=expiration_date_threshold)

    for membership in memberships_to_expire_soon:
        member = membership.member
        send_email(
            member=member, 
            messageType='SUBSCRIPTION_WARNING',
            subjectProp='Aviso de Expiração',
            messageProp=f"Olá {member.first_name},\n\nSua subscrição está prestes a expirar. Por favor, renove sua subscrição para continuar desfrutando dos nossos serviços.\n\nAtenciosamente,\nA equipe da Melgym")    

    return 'done'


def send_email(messageType, member, subjectProp, messageProp):
    try:
        preferences = Preferences.objects.get(messageType=messageType)
        subject = preferences.subject
        message = preferences.message.format(member_first_name=member.first_name)
    except Preferences.DoesNotExist:
        subject = subjectProp
        message = messageProp
    
    to_email = member.email
    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [to_email],
        fail_silently=False
    )
