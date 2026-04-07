import json
import urllib.request
from django.core.management.base import BaseCommand
from main_florife.models import VersiculoBiblia

class Command(BaseCommand):
    help = 'Importa la Biblia Reina Valera 1960 (RVR1960) desde un archivo JSON remoto'

    def handle(self, *args, **options):
        url = "https://raw.githubusercontent.com/thiagobodruk/bible/master/json/es_rvr.json"
        
        self.stdout.write(f'Descargando Biblia desde {url}...')
        try:
            with urllib.request.urlopen(url) as response:
                data = json.loads(response.read().decode('utf-8-sig'))
        except Exception as e:
            self.stderr.write(f'Error al descargar o procesar el JSON: {e}')
            return

        # thiagobodruk/bible format is usually a list of books
        # Each book: {"abbrev": "gn", "chapters": [[vs1, vs2, ...], [vs1, ...]], "name": "Gênesis"}
        
        versiculos_objects = []
        version_id = 'rv1960'
        
        # Mapping index to book number (standard 1-66)
        # Note: thiagobodruk/bible typically follows the order: 
        # 0: Gen, 1: Exod, ..., 65: Rev
        
        self.stdout.write('Procesando libros y capítulos...')
        
        # Boring but necessary: mapping for ensure book numbers match what we have in LibroBiblia
        # although thiagobodruk usually follows standard order
        
        for book_idx, book_data in enumerate(data):
            libro_num = book_idx + 1
            book_name = book_data.get('name')
            chapters = book_data.get('chapters', [])
            
            for cap_idx, chapter_verses in enumerate(chapters):
                cap_num = cap_idx + 1
                for vs_idx, text in enumerate(chapter_verses):
                    vs_num = vs_idx + 1
                    
                    versiculos_objects.append(VersiculoBiblia(
                        version=version_id,
                        libro=libro_num,
                        capitulo=cap_num,
                        versiculo=vs_num,
                        texto=text
                    ))
                    
        self.stdout.write(f'Borrando registros antiguos de {version_id}...')
        VersiculoBiblia.objects.filter(version=version_id).delete()
        
        self.stdout.write(f'Insertando {len(versiculos_objects)} versículos...')
        
        # Bulk create in chunks of 5000 to avoid memory/buffer issues
        chunk_size = 5000
        for i in range(0, len(versiculos_objects), chunk_size):
            VersiculoBiblia.objects.bulk_create(versiculos_objects[i:i+chunk_size])
            self.stdout.write(f'  - Insertados {min(i+chunk_size, len(versiculos_objects))}...')
            
        self.stdout.write(self.style.SUCCESS(f'¡Éxito! Biblia {version_id} importada correctamente.'))
