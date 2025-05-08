"""
WSGI config for Gym project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.0/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gym.settings')

application = get_wsgi_application()

# Configura o crontab quando a aplicação inicia
try:
    from django.core.management import call_command
    call_command('crontab', 'add')
except Exception as e:
    print(f"Erro ao iniciar configurações adicionais: {str(e)}")
