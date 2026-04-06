import csv
import os
import re
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import transaction
from main_florife.models import PalabraBiblia, TraduccionLiteral, Morfologia

class Command(BaseCommand):
    help = 'Importa la Biblia desde archivos CSV (base_biblia, interlinear_traduccion_literal, morfologia)'

    def handle(self, *args, **kwargs):
        base_dir = settings.BASE_DIR
        biblia_folder = os.path.join(base_dir, 'biblia')
        
        file_base = os.path.join(biblia_folder, 'base_biblia.csv')
        file_trad = os.path.join(biblia_folder, 'interlinear_traduccion_literal.csv')
        file_morf = os.path.join(biblia_folder, 'morfologia.csv')
        file_lownida = os.path.join(biblia_folder, 'lownida.csv')
        
        if not os.path.exists(file_base):
            self.stdout.write(self.style.ERROR(f'No se encontró {file_base}'))
            return

        self.stdout.write(self.style.SUCCESS('Comenzando la importación. Esto puede tardar unos minutos...'))

        # Leer Traducción y Morfología primero para crear todo en memoria
        self.stdout.write('Cargando interlinear_traduccion_literal.csv en memoria...')
        traduccion_dict = {}
        with open(file_trad, 'r', encoding='utf-8-sig', errors='ignore') as f:
            reader = csv.reader(f, delimiter='\t')
            next(reader) # skip header
            for row in reader:
                if len(row) >= 2:
                    traduccion_dict[row[0]] = row[1]
                    
        self.stdout.write('Cargando morfologia.csv en memoria...')
        morfologia_dict = {}
        with open(file_morf, 'r', encoding='utf-8-sig', errors='ignore') as f:
            reader = csv.reader(f, delimiter='\t')
            next(reader) # skip header
            for row in reader:
                if len(row) >= 4:
                    morfologia_dict[row[0]] = {'strong': row[1], 'rmac': row[2], 'desc': row[3]}

        clean_regex = re.compile(r'[〔〕]')
        
        self.stdout.write('Cargando lownida.csv en memoria para LouwNidaNumbers y Griego...')
        lownida_dict = {}
        with open(file_lownida, 'r', encoding='utf-8-sig', errors='ignore') as f:
            reader = csv.reader(f, delimiter='\t')
            next(reader) # skip header
            for row in reader:
                if len(row) > 8:
                    ln_num = None
                    griego_word = None
                    raiz_word = None
                    
                    # Columna 8: 〔BDAGentry...｜LN-LouwNidaNumbers〕
                    col8 = clean_regex.sub('', row[8])
                    parts8 = col8.split('｜')
                    if len(parts8) >= 5:
                        ln_num = parts8[4].strip()
                        
                    # Columna 7: 〔OGNTk｜OGNTu｜OGNTa｜lexeme｜rmac｜sn〕
                    col7 = clean_regex.sub('', row[7])
                    parts7 = col7.split('｜')
                    if len(parts7) >= 3:
                        griego_word = parts7[2].strip()
                    if len(parts7) >= 4:
                        raiz_word = parts7[3].strip()
                        
                    lownida_dict[row[0]] = {
                        'ln_num': ln_num,
                        'griego': griego_word,
                        'raiz_griega': raiz_word
                    }
                        
        self.stdout.write('Procesando base_biblia.csv y preparando objetos para la base de datos...')
        
        palabra_objects = []
        traduccion_objects = []
        morfologia_objects = []
        
        # Regex para limpiar 〔 y 〕 
        clean_regex = re.compile(r'[〔〕]')
        
        with open(file_base, 'r', encoding='utf-8-sig', errors='ignore') as f:
            reader = csv.reader(f, delimiter='\t')
            next(reader) # skip header
            
            for row in reader:
                if len(row) < 7:
                    continue
                    
                ognt_sort = row[0]
                bcv = row[6] # 〔Book｜Chapter｜Verse〕
                
                # Limpiar caracteres especiales
                bcv_clean = clean_regex.sub('', bcv)
                bcv_parts = bcv_clean.split('｜')
                
                if len(bcv_parts) != 3:
                    continue
                
                try:
                    libro = int(bcv_parts[0])
                    capitulo = int(bcv_parts[1])
                    versiculo = int(bcv_parts[2])
                except ValueError:
                    continue
                
                palabra = PalabraBiblia(
                    ognt_sort=ognt_sort,
                    libro=libro,
                    capitulo=capitulo,
                    versiculo=versiculo
                )
                palabra_objects.append(palabra)
                
                if ognt_sort in traduccion_dict:
                    traduccion_objects.append(TraduccionLiteral(
                        palabra=palabra,
                        espanol=traduccion_dict[ognt_sort],
                        griego=lownida_dict.get(ognt_sort, {}).get('griego', None),
                        raiz_griega=lownida_dict.get(ognt_sort, {}).get('raiz_griega', None)
                    ))
                
                if ognt_sort in morfologia_dict:
                    morf_data = morfologia_dict[ognt_sort]
                    morfologia_objects.append(Morfologia(
                        palabra=palabra,
                        rmac=morf_data['rmac'],
                        descripcion_rmac=morf_data['desc'],
                        low_nida_number=lownida_dict.get(ognt_sort, {}).get('ln_num', None),
                        strong=morf_data.get('strong', None)
                    ))

        self.stdout.write('Borrando datos antiguos si existen...')
        with transaction.atomic():
            Morfologia.objects.all().delete()
            TraduccionLiteral.objects.all().delete()
            PalabraBiblia.objects.all().delete()
            
            self.stdout.write(f'Insertando {len(palabra_objects)} PalabraBiblia...')
            PalabraBiblia.objects.bulk_create(palabra_objects, batch_size=5000)
            
            self.stdout.write(f'Insertando {len(traduccion_objects)} TraduccionLiteral...')
            TraduccionLiteral.objects.bulk_create(traduccion_objects, batch_size=5000)
            
            self.stdout.write(f'Insertando {len(morfologia_objects)} Morfologia...')
            Morfologia.objects.bulk_create(morfologia_objects, batch_size=5000)

        self.stdout.write(self.style.SUCCESS('¡Importación completada con éxito!'))
