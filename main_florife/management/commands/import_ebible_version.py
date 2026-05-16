import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from main_florife.models import VersiculoBiblia

VERSION_MAP = {
    'spa_r09': {'file': 'spa_r09.json', 'name': 'Reina Valera 1909'},
    'spa_bes': {'file': 'spa_bes.json', 'name': 'Biblia Española, Traducción Interconfesional (BES)'},
    'spa_blm': {'file': 'spa_blm.json', 'name': 'La Biblia de las Américas (LBLA)'},
    'spa_pdt': {'file': 'spa_pdt.json', 'name': 'Palabra de Dios para Todos (PDT)'},
    'spa_rvg': {'file': 'spa_rvg.json', 'name': 'Reina Valera Gómez (RVG)'},
    'BSB': {'file': 'BSB.json', 'name': 'Berean Standard Bible (BSB)'},
}


class Command(BaseCommand):
    help = 'Importa una versión bíblica desde archivo JSON (formato eBible.org)'

    def add_arguments(self, parser):
        parser.add_argument('--version-id', required=True,
                            help='Clave de la versión: ' + ', '.join(VERSION_MAP.keys()))
        parser.add_argument('--force', action='store_true',
                            help='Reimporta aunque ya existan registros')

    def handle(self, *args, **options):
        version_id = options['version_id']
        force = options.get('force', False)

        if version_id not in VERSION_MAP:
            self.stderr.write(f'Versión no reconocida: {version_id}')
            self.stderr.write(f'Opciones: {", ".join(VERSION_MAP.keys())}')
            return

        file_name = VERSION_MAP[version_id]['file']
        version_name = VERSION_MAP[version_id]['name']
        file_path = os.path.join(settings.BASE_DIR, 'data', file_name)

        if not os.path.exists(file_path):
            self.stderr.write(f'No se encontró el archivo: {file_path}')
            return

        existing = VersiculoBiblia.objects.filter(version=version_id).count()
        if existing > 0 and not force:
            self.stdout.write(f'Ya existen {existing} versículos para {version_id}.')
            self.stdout.write('Usa --force para reimportar.')
            return

        self.stdout.write(f'Leyendo {file_name}...')
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.stdout.write(f'Importando {version_name} ({version_id})...')

        def extract_text(items):
            parts = []
            for item in items:
                if isinstance(item, str):
                    parts.append(item)
                elif isinstance(item, dict):
                    if 'text' in item:
                        parts.append(item['text'])
            return ' '.join(parts)

        versiculos = []
        for book in data['books']:
            libro_num = book['order']
            for chapter_data in book['chapters']:
                cap_num = chapter_data['chapter']['number']
                for verse in chapter_data['chapter']['content']:
                    if verse.get('type') != 'verse':
                        continue
                    vs_num = verse['number']
                    text = extract_text(verse['content'])
                    versiculos.append(VersiculoBiblia(
                        version=version_id,
                        libro=libro_num,
                        capitulo=cap_num,
                        versiculo=vs_num,
                        texto=text
                    ))

        if not versiculos:
            self.stderr.write('No se encontraron versículos en el archivo.')
            return

        VersiculoBiblia.objects.filter(version=version_id).delete()

        chunk_size = 5000
        total = len(versiculos)
        self.stdout.write(f'Insertando {total} versículos...')
        for i in range(0, total, chunk_size):
            VersiculoBiblia.objects.bulk_create(versiculos[i:i + chunk_size])
            hechos = min(i + chunk_size, total)
            self.stdout.write(f'  {hechos}/{total}...')

        self.stdout.write(self.style.SUCCESS(
            f'¡Listo! {total} versículos importados para {version_name} ({version_id}).'
        ))
