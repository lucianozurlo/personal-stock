"""
Backup del superusuario antes de migrar a Custom User Model (core.User).

Este script se usa ANTES de aplicar la migración de AbstractUser (tarea 3.2).
El backup generado en fixtures/superuser_backup.json se usará en tarea 3.3
para recrear el superusuario con el mismo email y password hash una vez que
la tabla auth_user sea reemplazada por core_user.
"""
import json
import os

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = 'Backup del superusuario actual antes de migrar a Custom User Model'

    def handle(self, *args, **options):
        User = get_user_model()
        superuser = User.objects.filter(is_superuser=True).first()

        if not superuser:
            self.stderr.write(
                self.style.ERROR(
                    'Error: no se encontró ningún superusuario en la base de datos.'
                )
            )
            raise SystemExit(1)

        backup_data = {
            'email': superuser.email,
            'password': superuser.password,  # almacenado ya hasheado por Django
            'first_name': superuser.first_name,
            'last_name': superuser.last_name,
            'is_staff': superuser.is_staff,
            'is_superuser': superuser.is_superuser,
        }

        # Ruta relativa al directorio fixtures/ dentro de app/
        commands_dir = os.path.dirname(os.path.abspath(__file__))
        app_dir = os.path.dirname(os.path.dirname(os.path.dirname(commands_dir)))
        fixtures_dir = os.path.join(app_dir, 'fixtures')
        os.makedirs(fixtures_dir, exist_ok=True)

        output_path = os.path.join(fixtures_dir, 'superuser_backup.json')

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False)

        self.stdout.write(
            self.style.SUCCESS(
                f'Backup guardado en {output_path} — email: {superuser.email}'
            )
        )
