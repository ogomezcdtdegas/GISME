from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import IntegrityError

class Command(BaseCommand):
    help = 'Agrega un usuario a la plataforma GISME para permitir acceso'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='Email del usuario')
        parser.add_argument('--first-name', type=str, help='Nombre del usuario', default='')
        parser.add_argument('--last-name', type=str, help='Apellido del usuario', default='')
        parser.add_argument('--is-staff', action='store_true', help='Marcar como staff')
        parser.add_argument('--is-superuser', action='store_true', help='Marcar como superusuario')

    def handle(self, *args, **options):
        User = get_user_model()
        email = options['email']
        
        try:
            # Verificar si el usuario ya existe
            if User.objects.filter(email=email).exists():
                self.stdout.write(
                    self.style.WARNING(f'El usuario con email {email} ya existe en la plataforma.')
                )
                return
            
            # Crear el usuario
            user = User.objects.create(
                username=email,  # Usamos email como username por defecto
                email=email,
                first_name=options.get('first_name', ''),
                last_name=options.get('last_name', ''),
                is_staff=options.get('is_staff', False),
                is_superuser=options.get('is_superuser', False),
                is_active=True
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'Usuario {email} agregado exitosamente a la plataforma.')
            )
            
            if options.get('is_staff'):
                self.stdout.write(f'  - Marcado como staff: SÍ')
            if options.get('is_superuser'):
                self.stdout.write(f'  - Marcado como superusuario: SÍ')
                
        except IntegrityError as e:
            self.stdout.write(
                self.style.ERROR(f'Error al crear el usuario: {e}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error inesperado: {e}')
            )
