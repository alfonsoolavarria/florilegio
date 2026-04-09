import json
import os
from django.core.management.base import BaseCommand
from main_florife.models import VersiculoBiblia, ApiBibleSyncStatus
from django.db import transaction

class Command(BaseCommand):
    help = 'Exporta o importa versiones de la Biblia entre entornos'

    def add_arguments(self, parser):
        parser.add_argument('--export', type=str, help='Codigo de version a exportar (ej: nbla, rv1960)')
        parser.add_argument('--import_file', type=str, help='Ruta del archivo JSON a importar')

    def handle(self, *args, **options):
        export_version = options.get('export')
        import_file = options.get('import_file')

        if export_version:
            self.export_data(export_version)
        elif import_file:
            self.import_data(import_file)
        else:
            self.stdout.write(self.style.ERROR('Debe especificar --export <version> o --import_file <archivo>'))

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

    def import_data(self, file_path):
        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'Archivo no encontrado: {file_path}'))
            return

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

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
