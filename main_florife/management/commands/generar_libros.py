import json
from django.core.management.base import BaseCommand
from django.db.models import Max
from main_florife.models import LibroBiblia, VersiculoBiblia
from django.db import transaction

class Command(BaseCommand):
    help = 'Genera y llena la tabla LibroBiblia con la estructura de capítulos basada en los versículos importados.'

    def handle(self, *args, **kwargs):
        # Mapeo oficial de los libros del Nuevo Testamento
        NT_BOOKS = {
            40: "Mateo", 41: "Marcos", 42: "Lucas", 43: "Juan", 44: "Hechos",
            45: "Romanos", 46: "1 Corintios", 47: "2 Corintios", 48: "Gálatas", 49: "Efesios",
            50: "Filipenses", 51: "Colosenses", 52: "1 Tesalonicenses", 53: "2 Tesalonicenses",
            54: "1 Timoteo", 55: "2 Timoteo", 56: "Tito", 57: "Filemón", 58: "Hebreos",
            59: "Santiago", 60: "1 Pedro", 61: "2 Pedro", 62: "1 Juan", 63: "2 Juan",
            64: "3 Juan", 65: "Judas", 66: "Apocalipsis"
        }
        
        self.stdout.write("Calculando estructuras y generando registros para LibroBiblia...")

        with transaction.atomic():
            # Limpiar libros existentes para no tener duplicados o datos viejos
            LibroBiblia.objects.all().delete()
            
            libros_creados = 0
            
            for numero_libro, nombre in NT_BOOKS.items():
                # Filtrar todos los versículos que pertenecen a este libro
                versiculos_libro = VersiculoBiblia.objects.filter(libro=numero_libro)
                
                if not versiculos_libro.exists():
                    self.stdout.write(self.style.WARNING(f"  [!] Saltando {nombre} (No hay versículos en DB)"))
                    continue
                
                # Obtener la cantidad de versículos por capítulo dinámicamente
                capitulos_distintos = versiculos_libro.values_list('capitulo', flat=True).distinct().order_by('capitulo')
                
                estructura = {}
                for c_num in capitulos_distintos:
                    max_v = versiculos_libro.filter(capitulo=c_num).aggregate(Max('versiculo'))['versiculo__max']
                    estructura[str(c_num)] = max_v
                    
                LibroBiblia.objects.create(
                    numero=numero_libro,
                    nombre=nombre,
                    testamento="Nuevo Testamento",
                    estructura_capitulos=estructura
                )
                
                libros_creados += 1
                self.stdout.write(self.style.SUCCESS(f"  [✓] {nombre}: {len(estructura)} capítulos registrados."))

        if libros_creados > 0:
            self.stdout.write(self.style.SUCCESS(f'\n¡Éxito! Se crearon {libros_creados} libros en la base de datos.'))
        else:
            self.stdout.write(self.style.ERROR('\nNo se creó ningún libro. Asegúrate de ejecutar `python manage.py import_rv1960` primero.'))
