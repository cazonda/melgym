from django.core.management.base import BaseCommand
from django_crontab import CronJobManager

class Command(BaseCommand):
    help = 'Configura os jobs do crontab'

    def handle(self, *args, **options):
        # Remove todos os jobs existentes
        CronJobManager().remove_all()
        
        # Adiciona os jobs novamente
        CronJobManager().add_all()
        
        self.stdout.write(self.style.SUCCESS('Crontab jobs configurados com sucesso!')) 