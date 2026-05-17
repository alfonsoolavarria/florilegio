import os
import re
import xml.etree.ElementTree as ET
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db import transaction
from main_florife.models import PalabraHebreo, TraduccionHebreo, MorfologiaHebreo

BOOK_NUMBER_MAP = {
    'Gen': 1, 'Exod': 2, 'Lev': 3, 'Num': 4, 'Deut': 5,
    'Josh': 6, 'Judg': 7, 'Ruth': 8, '1Sam': 9, '2Sam': 10,
    '1Kgs': 11, '2Kgs': 12, '1Chr': 13, '2Chr': 14, 'Ezra': 15,
    'Neh': 16, 'Esth': 17, 'Job': 18, 'Ps': 19, 'Prov': 20,
    'Eccl': 21, 'Song': 22, 'Isa': 23, 'Jer': 24, 'Lam': 25,
    'Ezek': 26, 'Dan': 27, 'Hos': 28, 'Joel': 29, 'Amos': 30,
    'Obad': 31, 'Jonah': 32, 'Mic': 33, 'Nah': 34, 'Hab': 35,
    'Zeph': 36, 'Hag': 37, 'Zech': 38, 'Mal': 39,
}

NS = {'osis': 'http://www.bibletechnologies.net/2003/OSIS/namespace'}
STRONG_RE = re.compile(r'(\d+)')


def extract_strong(lemma):
    match = STRONG_RE.search(lemma)
    if match:
        return 'H' + match.group(1)
    return None


def clean_hebrew(text):
    return text.strip()


class Command(BaseCommand):
    help = 'Importa datos del morphhb (Hebrew OT interlinear) desde archivos XML'

    def add_arguments(self, parser):
        parser.add_argument('morphhb_dir', type=str, help='Ruta al directorio raiz del repositorio morphhb (contiene wlc/)')

    def handle(self, *args, **options):
        morphhb_dir = options['morphhb_dir']
        wlc_dir = os.path.join(morphhb_dir, 'wlc')

        if not os.path.isdir(wlc_dir):
            raise CommandError(f'No se encontro el directorio wlc/ en {morphhb_dir}')

        xml_files = sorted([f for f in os.listdir(wlc_dir) if f.endswith('.xml') and f != 'VerseMap.xml'])

        self.stdout.write(f'Encontrados {len(xml_files)} libros XML para importar')

        self.stdout.write('Borrando datos antiguos...')
        MorfologiaHebreo.objects.all().delete()
        TraduccionHebreo.objects.all().delete()
        PalabraHebreo.objects.all().delete()

        total_words = 0

        for filename in xml_files:
            filepath = os.path.join(wlc_dir, filename)
            book_key = filename.replace('.xml', '')
            libro_num = BOOK_NUMBER_MAP.get(book_key)

            if libro_num is None:
                self.stdout.write(self.style.WARNING(f'Saltando {filename}: libro no mapeado'))
                continue

            self.stdout.write(f'Procesando {filename} (libro {libro_num})...', ending=' ')
            self.stdout.flush()

            tree = ET.parse(filepath)
            root = tree.getroot()

            book_div = root.find('.//osis:div[@type="book"]', NS)
            if book_div is None:
                self.stdout.write(self.style.WARNING('No se encontro div type="book", saltando'))
                continue

            chapters = book_div.findall('osis:chapter', NS)

            palabra_objects = []
            traduccion_objects = []
            morfologia_objects = []
            word_count = 0

            for chapter_elem in chapters:
                chapter_osis = chapter_elem.get('osisID', '')
                try:
                    capitulo = int(chapter_osis.split('.')[-1])
                except (ValueError, IndexError):
                    continue

                verses = chapter_elem.findall('osis:verse', NS)
                for verse_elem in verses:
                    verse_osis = verse_elem.get('osisID', '')
                    try:
                        versiculo = int(verse_osis.split('.')[-1])
                    except (ValueError, IndexError):
                        continue

                    words = verse_elem.findall('osis:w', NS)
                    for orden, w_elem in enumerate(words, 1):
                        oshb_id = w_elem.get('id')
                        if not oshb_id:
                            continue

                        hebrew_text = clean_hebrew(w_elem.text or '')
                        if not hebrew_text:
                            continue

                        lemma = w_elem.get('lemma', '')
                        morph = w_elem.get('morph', '')
                        strong = extract_strong(lemma)

                        palabra = PalabraHebreo(
                            oshb_id=oshb_id,
                            libro=libro_num,
                            capitulo=capitulo,
                            versiculo=versiculo,
                            orden=orden,
                        )
                        palabra_objects.append(palabra)

                        traduccion_objects.append(TraduccionHebreo(
                            palabra=palabra,
                            hebreo=hebrew_text,
                            raiz_hebrea=None,
                            espanol=None,
                        ))

                        morfologia_objects.append(MorfologiaHebreo(
                            palabra=palabra,
                            morph_code=morph,
                            strong=strong,
                        ))

                        word_count += 1

            with transaction.atomic():
                PalabraHebreo.objects.bulk_create(palabra_objects, batch_size=5000)
                TraduccionHebreo.objects.bulk_create(traduccion_objects, batch_size=5000)
                MorfologiaHebreo.objects.bulk_create(morfologia_objects, batch_size=5000)

            total_words += word_count
            self.stdout.write(self.style.SUCCESS(f'{word_count} palabras'))

        self.stdout.write(self.style.SUCCESS(f'\n¡Importacion completada! {total_words} palabras en {len(xml_files)} libros'))
