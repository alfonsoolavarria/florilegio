import re
import sqlite3
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from main_florife.models import StrongConcord

STRONG_RE = re.compile(r'\([^{}()]+?,\s*(\d+)\)')


class Command(BaseCommand):
    help = 'Importa datos de Strong/Vine desde BibliaKoine.db SQLite a PostgreSQL'

    def handle(self, *args, **options):
        db_path = os.path.join(settings.BASE_DIR, "BibliaKoine.db")

        if not os.path.exists(db_path):
            self.stderr.write(f'No se encontró la base de datos: {db_path}')
            return

        self.stdout.write(f'Conectando a {db_path}...')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT topic, definition, is_strong, is_concord FROM strong_concord")
        rows = cursor.fetchall()
        conn.close()

        self.stdout.write(f'Leídos {len(rows)} registros de SQLite.')

        # Limpiar datos existentes en PostgreSQL
        count_before = StrongConcord.objects.count()
        if count_before > 0:
            self.stdout.write(f'Limpiando {count_before} registros existentes en PostgreSQL...')
            StrongConcord.objects.all().delete()

        objects = []
        for topic, definition, is_strong, is_concord in rows:
            m = STRONG_RE.search(definition) if definition else None
            strong_numbers = [int(m[1])] if m else []
            objects.append(StrongConcord(
                topic=topic,
                definition=definition,
                is_strong=bool(is_strong),
                is_concord=bool(is_concord),
                strong_numbers=strong_numbers,
            ))

        chunk_size = 5000
        for i in range(0, len(objects), chunk_size):
            StrongConcord.objects.bulk_create(objects[i:i + chunk_size])
            self.stdout.write(f'  - Insertados {min(i + chunk_size, len(objects))}...')

        self.stdout.write(self.style.SUCCESS(
            f'¡Éxito! {len(objects)} registros de Strong/Vine importados correctamente.'
        ))
