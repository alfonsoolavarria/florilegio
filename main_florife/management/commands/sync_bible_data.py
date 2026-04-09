import json
import os
from django.core.management.base import BaseCommand
from main_florife.models import VersiculoBiblia, ApiBibleSyncStatus
from django.db import transaction

class Command(BaseCommand):
    help = 'Exporta o importa versiones de la Biblia entre entornos'

    def add_arguments(self, parser):
        parser.add_argument('--export', type=str, help='Codigo de version a exportar (ej: nbla, rv1960)')
        parser.add_argument('--export_categories', action='store_true', help='Exporta todas las categorias y sus iconos')
        parser.add_argument('--import_file', type=str, help='Ruta del archivo JSON a importar')

    def handle(self, *args, **options):
        export_version = options.get('export')
        export_categories = options.get('export_categories')
        import_file = options.get('import_file')

        if export_version:
            self.export_data(export_version)
        elif export_categories:
            self.export_categories()
        elif import_file:
            self.import_data(import_file)
        else:
            self.stdout.write(self.style.ERROR('Debe especificar --export <version>, --export_categories o --import_file <archivo>'))

    def export_data(self, version):
        self.stdout.write(f'Exportando version: {version}...')
        
        # Obtener versículos
        verses = VersiculoBiblia.objects.filter(version=version).values(
            'version', 'libro', 'capitulo', 'versiculo', 'texto'
        )
        
        # Obtener estado de sincronización si existe
        sync_status = ApiBibleSyncStatus.objects.filter(version=version).values('version', 'last_synced_at')
        
        data = {
            'version': version,
            'sync_status': list(sync_status),
            'verses': list(verses)
        }
        
        filename = f'{version}_backup.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        
        self.stdout.write(self.style.SUCCESS(f'Exportación completada: {filename} ({len(data["verses"])} versículos)'))

    def export_categories(self):
        from main_florife.models import Category
        self.stdout.write('Exportando categorías e iconos...')
        categories = Category.objects.all().values('id', 'name', 'icon')
        
        data = {
            'type': 'categories',
            'categories': list(categories)
        }
        
        filename = 'categories_backup.json'
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        self.stdout.write(self.style.SUCCESS(f'Exportación de categorías completada: {filename}'))

    def import_data(self, file_path):
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'Archivo no encontrado: {file_path}'))
            return

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if data.get('type') == 'categories':
            self.import_categories(data)
            return

        version = data.get('version')
        verses_data = data.get('verses', [])
        sync_data = data.get('sync_status', [])

        self.stdout.write(f'Importando {len(verses_data)} versículos de la versión: {version}...')

        with transaction.atomic():
            # Limpiar datos previos de esta versión para evitar duplicados
            VersiculoBiblia.objects.filter(version=version).delete()
            
            # Crear objetos VersiculoBiblia
            to_create = [
                VersiculoBiblia(
                    version=v['version'],
                    libro=v['libro'],
                    capitulo=v['capitulo'],
                    versiculo=v['versiculo'],
                    texto=v['texto']
                ) for v in verses_data
            ]
            
            # Usar bulk_create para velocidad
            batch_size = 1000
            for i in range(0, len(to_create), batch_size):
                VersiculoBiblia.objects.bulk_create(to_create[i:i + batch_size])
                self.stdout.write(f'Procesados {min(i + batch_size, len(to_create))} versículos...')

            # Actualizar sync status
            if sync_data:
                ApiBibleSyncStatus.objects.update_or_create(
                    version=version,
                    defaults={'last_synced_at': sync_data[0]['last_synced_at']}
                )

        self.stdout.write(self.style.SUCCESS(f'Importación de {version} finalizada con éxito.'))

    def import_categories(self, data):
        from main_florife.models import Category
        categories_data = data.get('categories', [])
        self.stdout.write(f'Importando {len(categories_data)} categorías...')
        
        for c_data in categories_data:
            Category.objects.update_or_create(
                id=c_data['id'],
                defaults={'name': c_data['name'], 'icon': c_data['icon']}
            )
            
        self.stdout.write(self.style.SUCCESS('Importación de categorías finalizada.'))

