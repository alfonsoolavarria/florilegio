import json
from collections import Counter, defaultdict
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import transaction
from main_florife.models import PalabraHebreo, TraduccionHebreo, MorfologiaHebreo


def build_strong_to_spanish_map(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    word_by_strong = defaultdict(list)

    for slug, book in data.items():
        for ch_data in book['chapters'].values():
            for v in ch_data:
                for w in v['words']:
                    strong = w['strong']
                    word = w['word']
                    if strong.startswith('H'):
                        word_by_strong[strong[1:]].append(word)

    mapping = {}
    for strong, words in word_by_strong.items():
        if words:
            mapping[strong] = Counter(words).most_common(1)[0][0]
    return mapping


class Command(BaseCommand):
    help = 'Poblar TraduccionHebreo.espanol usando RV1960 con Strongs (scrapeado de bibliaya.com)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Actualizar todos los registros, no solo los nulos',
        )

    def handle(self, *args, **options):
        filepath = settings.BASE_DIR / 'rvs_strongs_ot.json'
        if not filepath.exists():
            self.stdout.write(self.style.ERROR(f'No se encontró {filepath}'))
            self.stdout.write('Ejecuta primero: python scrape_rvs_strongs.py')
            return

        force = options['force']

        self.stdout.write('Construyendo mapa Strong → español desde RV1960...')
        strong_map = build_strong_to_spanish_map(str(filepath))
        self.stdout.write(f'Mapa construido: {len(strong_map)} Strongs cubiertos')

        qs = TraduccionHebreo.objects.select_related('palabra__morfologia_hebreo')
        if not force:
            qs = qs.filter(espanol__isnull=True)

        total = 0
        actualizados = 0
        no_cubiertos = 0
        batch = []
        batch_size = 5000

        self.stdout.write('Actualizando TraduccionHebreo.espanol por lotes...')

        for th in qs.iterator(chunk_size=2000):
            total += 1
            strong = th.palabra.morfologia_hebreo.strong
            if strong and strong.startswith('H'):
                num = strong[1:]
                if num in strong_map:
                    th.espanol = strong_map[num]
                    batch.append(th)
                    actualizados += 1
                else:
                    no_cubiertos += 1
            else:
                no_cubiertos += 1

            if len(batch) >= batch_size:
                TraduccionHebreo.objects.bulk_update(batch, ['espanol'])
                batch = []
                self.stdout.write(f'  Procesados {total}... actualizados {actualizados}')

        if batch:
            TraduccionHebreo.objects.bulk_update(batch, ['espanol'])

        self.stdout.write(self.style.SUCCESS(
            f'Completado: {total} palabras procesadas, '
            f'{actualizados} actualizadas, '
            f'{no_cubiertos} sin cubrir'
        ))
