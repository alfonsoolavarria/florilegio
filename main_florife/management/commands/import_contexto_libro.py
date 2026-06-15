import json
import glob
import os
from django.conf import settings
from django.core.management.base import BaseCommand
from main_florife.models import ContextoLibro, LibroBiblia


JSON_MAP = {
    "Mateo": ["Mateo"],
    "Marcos": ["Marcos"],
    "Lucas": ["Lucas"],
    "Juan": ["Juan"],
    "Hechos": ["Hechos"],
    "Romanos": ["Romanos"],
    "1 Corintios": ["1 Corintios"],
    "2 Corintios": ["2 Corintios"],
    "Gálatas": ["Gálatas"],
    "Efesios": ["Efesios"],
    "Filipenses": ["Filipenses"],
    "Colosenses": ["Colosenses"],
    "1 y 2 Tesalonicenses": ["1 Tesalonicenses", "2 Tesalonicenses"],
    "1,2 Timoteo y Tito": ["1 Timoteo", "2 Timoteo", "Tito"],
    "Filemón": ["Filemón"],
    "Hebreos": ["Hebreos"],
    "Santiago": ["Santiago"],
    "1ra. de Pedro": ["1 Pedro"],
    "2da. de Pedro": ["2 Pedro"],
    "1 Juan": ["1 Juan"],
    "2 Juan": ["2 Juan"],
    "3 Juan": ["3 Juan"],
    "Judas": ["Judas"],
    "Apocalipsis": ["Apocalipsis"],
}


class Command(BaseCommand):
    help = "Importa los JSON de contexto biblico desde jsonBob/"

    def handle(self, *args, **options):
        ContextoLibro.objects.all().delete()
        base_dir = os.path.join(settings.BASE_DIR, "jsonBob")
        files = glob.glob(os.path.join(base_dir, "*.json"))
        created = 0

        tito_data = None
        tito_complement = None

        for fpath in sorted(files):
            with open(fpath, encoding="utf-8") as f:
                raw = f.read()
            data = json.loads(raw)
            libro_name = data["libro"]
            contenido_raw = json.dumps(data["contenido"], ensure_ascii=False)

            if libro_name == "Tito":
                tito_complement = data["contenido"]
                self.stdout.write(f"  Guardando complemento de Tito")
                continue

            db_names = JSON_MAP.get(libro_name)
            if not db_names:
                self.stdout.write(f"  LIBRO NO MAPEADO: {libro_name}")
                continue

            for db_name in db_names:
                libros = LibroBiblia.objects.filter(nombre=db_name, testamento="Nuevo Testamento")
                if not libros.exists():
                    self.stdout.write(f"  NO ENCONTRADO EN DB: {db_name}")
                    continue
                for libro in libros:
                    if libro_name == "1,2 Timoteo y Tito" and db_name == "Tito":
                        tito_data = contenido_raw
                    else:
                        ContextoLibro.objects.create(libro=libro, contenido=contenido_raw)
                        created += 1
                        self.stdout.write(f"  Creado: {libro.nombre}")

        # Tito: fusionar data principal + complemento
        libros_tito = LibroBiblia.objects.filter(nombre="Tito", testamento="Nuevo Testamento")
        if tito_data and tito_complement:
            tito_contenido = json.loads(tito_data)
            tito_contenido["tito_complemento"] = tito_complement
            merged = json.dumps(tito_contenido, ensure_ascii=False)
            for libro in libros_tito:
                ContextoLibro.objects.create(libro=libro, contenido=merged)
                created += 1
                self.stdout.write(f"  Creado: Tito (con complemento)")
        elif tito_data:
            for libro in libros_tito:
                ContextoLibro.objects.create(libro=libro, contenido=tito_data)
                created += 1
                self.stdout.write(f"  Creado: Tito (sin complemento)")
        elif tito_complement:
            merged = json.dumps({"tito_complemento": tito_complement}, ensure_ascii=False)
            for libro in libros_tito:
                ContextoLibro.objects.create(libro=libro, contenido=merged)
                created += 1
                self.stdout.write(f"  Creado: Tito (solo complemento)")

        self.stdout.write(self.style.SUCCESS(f"Importacion completa: {created} contextos creados"))
