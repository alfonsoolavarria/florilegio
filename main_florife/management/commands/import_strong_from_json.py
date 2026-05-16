import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from main_florife.models import StrongConcord


class Command(BaseCommand):
    help = 'Importa definiciones de Strong desde strong_hebreo.json y strong_griego.json a la tabla strong_concord'

    def handle(self, *args, **options):
        base = settings.BASE_DIR

        count_before = StrongConcord.objects.count()
        if count_before > 0:
            self.stdout.write(f'Limpiando {count_before} registros existentes...')
            StrongConcord.objects.all().delete()

        hebreo_path = os.path.join(base, 'strong_hebreo.json')
        griego_path = os.path.join(base, 'strong_griego.json')

        for fpath, lang, prefix in [
            (hebreo_path, 'hebreo', 'H'),
            (griego_path, 'griego', 'G'),
        ]:
            if not os.path.exists(fpath):
                self.stderr.write(f'No se encontró {fpath}')
                return

            with open(fpath) as f:
                data = json.load(f)
            key = list(data.keys())[0]
            entries = data[key]
            self.stdout.write(f'Cargando {len(entries)} entradas de strong_{lang}.json...')

            objects = []
            for entry in entries:
                strong_num = entry['strong']
                topic = f'{prefix}{strong_num}'
                definition = entry.get('definicion', '')
                objects.append(StrongConcord(
                    topic=topic,
                    definition=definition,
                    is_strong=True,
                    is_concord=False,
                    strong_numbers=[int(strong_num)],
                ))

            chunk_size = 5000
            for i in range(0, len(objects), chunk_size):
                StrongConcord.objects.bulk_create(objects[i:i + chunk_size], ignore_conflicts=True)
                self.stdout.write(f'  - Insertados {min(i + chunk_size, len(objects))}...')

        total = StrongConcord.objects.count()
        self.stdout.write(self.style.SUCCESS(
            f'¡Éxito! {total} registros de Strong importados correctamente en strong_concord.'
        ))
