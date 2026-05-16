import json
from django.core.management.base import BaseCommand
from django.db.models import Max
from main_florife.models import LibroBiblia, VersiculoBiblia
from django.db import transaction

class Command(BaseCommand):
    help = 'Genera y llena la tabla LibroBiblia con la estructura de capítulos basada en los versículos importados.'

    def handle(self, *args, **kwargs):
        ALL_BOOKS = {
            1: ("Génesis", "Antiguo Testamento"),
            2: ("Éxodo", "Antiguo Testamento"),
            3: ("Levítico", "Antiguo Testamento"),
            4: ("Números", "Antiguo Testamento"),
            5: ("Deuteronomio", "Antiguo Testamento"),
            6: ("Josué", "Antiguo Testamento"),
            7: ("Jueces", "Antiguo Testamento"),
            8: ("Rut", "Antiguo Testamento"),
            9: ("1 Samuel", "Antiguo Testamento"),
            10: ("2 Samuel", "Antiguo Testamento"),
            11: ("1 Reyes", "Antiguo Testamento"),
            12: ("2 Reyes", "Antiguo Testamento"),
            13: ("1 Crónicas", "Antiguo Testamento"),
            14: ("2 Crónicas", "Antiguo Testamento"),
            15: ("Esdras", "Antiguo Testamento"),
            16: ("Nehemías", "Antiguo Testamento"),
            17: ("Ester", "Antiguo Testamento"),
            18: ("Job", "Antiguo Testamento"),
            19: ("Salmos", "Antiguo Testamento"),
            20: ("Proverbios", "Antiguo Testamento"),
            21: ("Eclesiastés", "Antiguo Testamento"),
            22: ("Cantar de los Cantares", "Antiguo Testamento"),
            23: ("Isaías", "Antiguo Testamento"),
            24: ("Jeremías", "Antiguo Testamento"),
            25: ("Lamentaciones", "Antiguo Testamento"),
            26: ("Ezequiel", "Antiguo Testamento"),
            27: ("Daniel", "Antiguo Testamento"),
            28: ("Oseas", "Antiguo Testamento"),
            29: ("Joel", "Antiguo Testamento"),
            30: ("Amós", "Antiguo Testamento"),
            31: ("Abdías", "Antiguo Testamento"),
            32: ("Jonás", "Antiguo Testamento"),
            33: ("Miqueas", "Antiguo Testamento"),
            34: ("Nahum", "Antiguo Testamento"),
            35: ("Habacuc", "Antiguo Testamento"),
            36: ("Sofonías", "Antiguo Testamento"),
            37: ("Hageo", "Antiguo Testamento"),
            38: ("Zacarías", "Antiguo Testamento"),
            39: ("Malaquías", "Antiguo Testamento"),
            40: ("Mateo", "Nuevo Testamento"),
            41: ("Marcos", "Nuevo Testamento"),
            42: ("Lucas", "Nuevo Testamento"),
            43: ("Juan", "Nuevo Testamento"),
            44: ("Hechos", "Nuevo Testamento"),
            45: ("Romanos", "Nuevo Testamento"),
            46: ("1 Corintios", "Nuevo Testamento"),
            47: ("2 Corintios", "Nuevo Testamento"),
            48: ("Gálatas", "Nuevo Testamento"),
            49: ("Efesios", "Nuevo Testamento"),
            50: ("Filipenses", "Nuevo Testamento"),
            51: ("Colosenses", "Nuevo Testamento"),
            52: ("1 Tesalonicenses", "Nuevo Testamento"),
            53: ("2 Tesalonicenses", "Nuevo Testamento"),
            54: ("1 Timoteo", "Nuevo Testamento"),
            55: ("2 Timoteo", "Nuevo Testamento"),
            56: ("Tito", "Nuevo Testamento"),
            57: ("Filemón", "Nuevo Testamento"),
            58: ("Hebreos", "Nuevo Testamento"),
            59: ("Santiago", "Nuevo Testamento"),
            60: ("1 Pedro", "Nuevo Testamento"),
            61: ("2 Pedro", "Nuevo Testamento"),
            62: ("1 Juan", "Nuevo Testamento"),
            63: ("2 Juan", "Nuevo Testamento"),
            64: ("3 Juan", "Nuevo Testamento"),
            65: ("Judas", "Nuevo Testamento"),
            66: ("Apocalipsis", "Nuevo Testamento"),
        }
        
        self.stdout.write("Calculando estructuras y generando registros para LibroBiblia (Antiguo + Nuevo Testamento)...")

        with transaction.atomic():
            LibroBiblia.objects.all().delete()
            
            libros_creados = 0
            
            for numero_libro, (nombre, testamento) in ALL_BOOKS.items():
                versiculos_libro = VersiculoBiblia.objects.filter(libro=numero_libro)
                
                if not versiculos_libro.exists():
                    self.stdout.write(self.style.WARNING(f"  [!] Saltando {nombre} (No hay versículos en DB)"))
                    continue
                
                capitulos_distintos = versiculos_libro.values_list('capitulo', flat=True).distinct().order_by('capitulo')
                
                estructura = {}
                for c_num in capitulos_distintos:
                    max_v = versiculos_libro.filter(capitulo=c_num).aggregate(Max('versiculo'))['versiculo__max']
                    estructura[str(c_num)] = max_v
                    
                LibroBiblia.objects.create(
                    numero=numero_libro,
                    nombre=nombre,
                    testamento=testamento,
                    estructura_capitulos=estructura
                )
                
                libros_creados += 1
                self.stdout.write(self.style.SUCCESS(f"  [✓] {nombre}: {len(estructura)} capítulos registrados."))

        if libros_creados > 0:
            self.stdout.write(self.style.SUCCESS(f'\n¡Éxito! Se crearon {libros_creados} libros en la base de datos.'))
        else:
            self.stdout.write(self.style.ERROR('\nNo se creó ningún libro. Asegúrate de ejecutar primero `python manage.py import_ebible_version` o similar.'))
