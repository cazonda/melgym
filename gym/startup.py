import os
import subprocess
from django.core.management import call_command

def setup_cron():
    """
    Configura os jobs do crontab quando a aplicação inicia
    """
    try:
        # Remove todos os jobs existentes
        call_command('crontab', 'remove')
        
        # Adiciona os jobs novamente
        call_command('crontab', 'add')
        
        print("Crontab jobs configurados com sucesso!")
    except Exception as e:
        print(f"Erro ao configurar crontab: {str(e)}")

# Esta função será chamada quando a aplicação iniciar
def startup():
    setup_cron() 