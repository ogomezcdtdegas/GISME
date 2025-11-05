from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db.models import Count

class Command(BaseCommand):
    help = 'Lista usuarios duplicados por email y permite limpiarlos'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clean',
            action='store_true',
            help='Eliminar usuarios duplicados, manteniendo solo el más reciente'
        )

    def handle(self, *args, **options):
        User = get_user_model()
        
        # Buscar emails duplicados
        duplicates = (
            User.objects
            .values('email')
            .annotate(count=Count('id'))
            .filter(count__gt=1)
            .exclude(email='')  # Excluir emails vacíos
        )
        
        if not duplicates:
            self.stdout.write(
                self.style.SUCCESS('No se encontraron usuarios duplicados.')
            )
            return
        
        self.stdout.write(f'Se encontraron {len(duplicates)} emails con usuarios duplicados:')
        
        for duplicate in duplicates:
            email = duplicate['email']
            count = duplicate['count']
            users = User.objects.filter(email=email).order_by('date_joined')
            
            self.stdout.write(f'\n📧 Email: {email} ({count} usuarios)')
            for i, user in enumerate(users):
                status = "🆔 MÁS RECIENTE" if i == count-1 else "🗑️  DUPLICADO"
                self.stdout.write(f'  - ID: {user.id}, Username: {user.username}, Creado: {user.date_joined} {status}')
            
            if options['clean']:
                # Eliminar todos excepto el más reciente
                users_to_delete = users[:-1]  # Todos excepto el último
                deleted_count = len(users_to_delete)
                users_to_delete.delete()
                
                self.stdout.write(
                    self.style.WARNING(f'  ✅ Eliminados {deleted_count} usuarios duplicados para {email}')
                )
        
        if not options['clean']:
            self.stdout.write(
                self.style.WARNING('\n💡 Para eliminar los duplicados, ejecuta: python manage.py clean_duplicates --clean')
            )
