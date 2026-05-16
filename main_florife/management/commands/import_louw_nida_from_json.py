import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from main_florife.models import LouwNidaConcord


class Command(BaseCommand):
    help = 'Importa definiciones de Louw-Nida desde louw_nida.json a la tabla louw_nida_concord'

    def handle(self, *args, **options):
        base = settings.BASE_DIR
        filepath = os.path.join(base, 'louw_nida.json')

        count_before = LouwNidaConcord.objects.count()
        if count_before > 0:
            self.stdout.write(f'Limpiando {count_before} registros existentes...')
            LouwNidaConcord.objects.all().delete()

        if not os.path.exists(filepath):
            self.stderr.write(f'No se encontró {filepath}')
            return

        with open(filepath, encoding='utf-8') as f:
            data = json.load(f)
        key = list(data.keys())[0]
        entries = data[key]
        self.stdout.write(f'Cargando {len(entries)} entradas de louw_nida.json...')

        objects = []
        for entry in entries:
            objects.append(LouwNidaConcord(
                id=entry['id'],
                termino_griego=entry.get('termino_griego', ''),
                definicion_completa=entry.get('definicion_completa', ''),
                glosa_principal=entry.get('glosa_principal', ''),
            ))

        chunk_size = 5000
        for i in range(0, len(objects), chunk_size):
            LouwNidaConcord.objects.bulk_create(objects[i:i + chunk_size], ignore_conflicts=True)
            self.stdout.write(f'  - Insertados {min(i + chunk_size, len(objects))}...')

        total = LouwNidaConcord.objects.count()
        self.stdout.write(self.style.SUCCESS(
            f'¡Éxito! {total} registros de Louw-Nida importados correctamente en louw_nida_concord.'
        ))
