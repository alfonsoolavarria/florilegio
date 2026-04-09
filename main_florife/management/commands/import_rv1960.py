import json
import os
from django.core.management.base import BaseCommand
from main_florife.models import VersiculoBiblia
from django.conf import settings

class Command(BaseCommand):
    help = 'Importa la Biblia Reina Valera 1960 (RV1960) real desde archivos locales'

    def handle(self, *args, **options):
        biblia_path = os.path.join(settings.BASE_DIR, "data", "biblia_rv1960")
        index_path = os.path.join(biblia_path, "index.json")

        
        self.stdout.write(f'Leyendo índice desde {index_path}...')
        try:
            with open(index_path, 'r', encoding='utf-8') as f:
                index_data = json.load(f)
        except Exception as e:
            self.stderr.write(f'Error al leer el índice JSON: {e}')
            return
        
        versiculos_objects = []
        version_id = 'rv1960'
        
        self.stdout.write('Procesando libros, capítulos y versículos...')
        
        for book_metadata in index_data:
            libro_num = book_metadata['number']
            book_key = book_metadata['key']
            book_name = book_metadata['title']
            
            book_file_path = os.path.join(biblia_path, f"{book_key}.json")
            try:
                with open(book_file_path, 'r', encoding='utf-8') as f:
                    book_chapters = json.load(f)
            except Exception as e:
                self.stderr.write(f'Error al leer el libro {book_name} ({book_file_path}): {e}')
                continue
                
            for cap_idx, chapter_verses in enumerate(book_chapters):
                cap_num = cap_idx + 1
                for vs_idx, text in enumerate(chapter_verses):
                    vs_num = vs_idx + 1
                    
                    clean_text = text.replace('_', '')
                    
                    versiculos_objects.append(VersiculoBiblia(
                        version=version_id,
                        libro=libro_num,
                        capitulo=cap_num,
                        versiculo=vs_num,
                        texto=clean_text
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